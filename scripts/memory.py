#!/usr/bin/env python3
"""Manage IntentClause's project-local, thresholded learning ledger."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import tempfile
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


MEMORY_RELATIVE = Path(".intent-clause") / "memory.jsonl"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}")
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"\b(?:sk|ghp|github_pat|AIza)[-_A-Za-z0-9]{12,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\b(?:postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.IGNORECASE | re.DOTALL),
)
ALLOWED_KINDS = {"correction", "success", "failure", "convention", "dead_end"}
ALLOWED_FEEDBACK = {"useful", "wrong", "stale", "dead_end"}
ALLOWED_STATUSES = {"candidate", "promoted", "stale", "deprecated"}
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def memory_path(root: Path) -> Path:
    root = root.resolve()
    if root.exists() and not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")
    parent = root / MEMORY_RELATIVE.parent
    if parent.exists():
        if parent.is_symlink() or not parent.resolve().is_relative_to(root):
            raise ValueError(f"memory directory escapes the project: {parent}")
        if not parent.is_dir():
            raise ValueError(f"memory path is not a directory: {parent}")
    ledger = root / MEMORY_RELATIVE
    if ledger.exists():
        if ledger.is_symlink() or not ledger.resolve().is_relative_to(root):
            raise ValueError(f"memory ledger escapes the project: {ledger}")
        if not ledger.is_file():
            raise ValueError(f"memory ledger is not a regular file: {ledger}")
    return ledger


def signing_key_path() -> Path:
    override = os.environ.get("INTENT_CLAUSE_KEY_FILE")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "intent-clause" / "memory.key"


def signing_key() -> bytes:
    environment_key = os.environ.get("INTENT_CLAUSE_SIGNING_KEY")
    if environment_key:
        try:
            key = bytes.fromhex(environment_key)
        except ValueError as exc:
            raise ValueError("INTENT_CLAUSE_SIGNING_KEY must be hexadecimal") from exc
        if len(key) < 32:
            raise ValueError("INTENT_CLAUSE_SIGNING_KEY must contain at least 32 bytes")
        return key

    path = signing_key_path()
    if path.is_symlink():
        raise ValueError(f"signing key must not be a symlink: {path}")
    if path.exists():
        if not path.is_file():
            raise ValueError(f"signing key is not a regular file: {path}")
        key = path.read_bytes()
        if len(key) != 32:
            raise ValueError(f"signing key has an invalid length: {path}")
        return key

    path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return signing_key()
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(key)
        handle.flush()
        os.fsync(handle.fileno())
    return key


def record_signature(record: dict[str, Any], key: bytes) -> str:
    unsigned = {name: value for name, value in record.items() if name != "signature"}
    payload = json.dumps(unsigned, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def validate_record(record: dict[str, Any], key: bytes, line_number: int) -> None:
    required = {
        "id", "kind", "summary", "normalized", "scope", "status", "verified",
        "confidence", "support_count", "evidence", "evidence_hashes",
        "evidence_fingerprint", "created_at", "updated_at", "feedback", "signature",
    }
    if not required.issubset(record):
        raise ValueError(f"memory record on line {line_number} is missing required fields")
    if record.get("kind") not in ALLOWED_KINDS or record.get("status") not in ALLOWED_STATUSES:
        raise ValueError(f"memory record on line {line_number} has invalid state")
    if not isinstance(record.get("summary"), str) or not isinstance(record.get("evidence_hashes"), dict):
        raise ValueError(f"memory record on line {line_number} has invalid field types")
    if record.get("normalized") != normalize(record["summary"]):
        raise ValueError(f"memory record on line {line_number} has an invalid normalized summary")
    expected_fingerprint = evidence_fingerprint(record["evidence_hashes"]) if record["evidence_hashes"] else None
    if record.get("evidence_fingerprint") != expected_fingerprint:
        raise ValueError(f"memory record on line {line_number} has an invalid evidence fingerprint")
    if record.get("status") == "promoted":
        if not record.get("verified") or not record["evidence_hashes"]:
            raise ValueError(f"promoted memory record on line {line_number} lacks verified evidence")
        if record.get("kind") in {"success", "failure", "dead_end"} and int(record.get("support_count", 0)) < 2:
            raise ValueError(f"promoted memory record on line {line_number} lacks independent support")
        if record.get("kind") == "convention" and len(record["evidence_hashes"]) < 2:
            raise ValueError(f"promoted convention on line {line_number} lacks two sources")
    signature = str(record.get("signature", ""))
    if not hmac.compare_digest(signature, record_signature(record, key)):
        raise ValueError(f"memory record on line {line_number} failed integrity verification")


def redact(text: str) -> str:
    value = text.strip()
    for index, pattern in enumerate(SECRET_PATTERNS):
        replacement = r"\1[REDACTED]" if index == 0 else "[REDACTED]"
        value = pattern.sub(replacement, value)
    return value


def clean_text(text: str, max_length: int) -> str:
    value = " ".join(redact(text).split())
    if not value:
        raise ValueError("text cannot be empty")
    return value[:max_length]


def normalize(text: str) -> str:
    return " ".join(sorted(set(token.lower() for token in TOKEN_PATTERN.findall(text))))


def file_hash(path: Path, root: Path | None = None) -> str | None:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        resolved = path.resolve()
        if root is not None and not resolved.is_relative_to(root.resolve()):
            return None
        if path.stat().st_size > MAX_EVIDENCE_BYTES:
            return None
        digest = hashlib.sha256()
        with resolved.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    key = signing_key()
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid memory record on line {number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"memory record on line {number} is not an object")
        validate_record(record, key, number)
        records.append(record)
    return records


def save_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = signing_key()
    for record in records:
        record["signature"] = record_signature(record, key)
    content = "".join(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n" for record in records)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".memory-", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() and (path.is_symlink() or not path.resolve().is_relative_to(path.parent.resolve())):
            raise ValueError(f"memory ledger changed to an unsafe path: {path}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def evidence_hashes(root: Path, evidence: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for raw in evidence[:20]:
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts:
            continue
        digest = file_hash(root / relative, root)
        if digest:
            hashes[relative.as_posix()] = digest
    return hashes


def stale_reason(root: Path, record: dict[str, Any]) -> str | None:
    hashes = record.get("evidence_hashes", {})
    if not isinstance(hashes, dict):
        return "invalid evidence fingerprints"
    for relative, expected in hashes.items():
        current = file_hash(root / relative, root)
        if current is None:
            return f"evidence missing: {relative}"
        if current != expected:
            return f"evidence changed: {relative}"
    return None


def reflect(root: Path, records: list[dict[str, Any]]) -> int:
    changed = 0
    for record in records:
        if record.get("status") not in {"candidate", "promoted"}:
            continue
        reason = stale_reason(root, record)
        if reason:
            record["status"] = "stale"
            record["stale_reason"] = reason
            record["updated_at"] = now()
            changed += 1
    return changed


def similarity(query: str, lesson: str) -> float:
    query_tokens = set(normalize(query).split())
    lesson_tokens = set(normalize(lesson).split())
    union = query_tokens | lesson_tokens
    jaccard = len(query_tokens & lesson_tokens) / len(union) if union else 0.0
    sequence = SequenceMatcher(None, query.lower(), lesson.lower()).ratio()
    return 0.75 * jaccard + 0.25 * sequence


def evidence_fingerprint(hashes: dict[str, str]) -> str:
    serialized = json.dumps(hashes, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def record_command(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    path = memory_path(root)
    records = load_records(path)
    reflect(root, records)

    summary = clean_text(args.summary, 800)
    scope = clean_text(args.scope, 200)
    evidence = [clean_text(value, 300) for value in args.evidence]
    normalized = normalize(summary)
    matching = [
        item for item in records
        if item.get("normalized") == normalized and item.get("status") in {"candidate", "promoted"}
    ]
    prior_run_ids = {str(item.get("run_id")) for item in matching if item.get("run_id")}
    if args.run_id and args.run_id in prior_run_ids:
        print(json.dumps({"stored": None, "reason": "duplicate run-id", "run_id": args.run_id}, indent=2))
        return
    verified = bool(args.verified)
    confidence = 0.9 if args.kind == "correction" and verified else 0.7 if verified else 0.35
    hashes = evidence_hashes(root, args.evidence)
    if verified and not hashes:
        raise ValueError("--verified requires at least one existing project-relative --evidence file")
    fingerprint = evidence_fingerprint(hashes) if hashes else None
    prior_fingerprints = {str(item.get("evidence_fingerprint")) for item in matching if item.get("evidence_fingerprint")}
    independent_repeat = bool(
        args.run_id
        and args.run_id not in prior_run_ids
        and fingerprint
        and fingerprint not in prior_fingerprints
    )
    support = 1 + min(len(prior_run_ids), len(prior_fingerprints)) if independent_repeat else max([int(item.get("support_count", 1)) for item in matching] or [1])
    promoted = verified and (
        args.kind == "correction"
        or support >= 2 and independent_repeat
        or len(hashes) >= 2 and args.kind == "convention"
    )
    timestamp = now()
    identifier = hashlib.sha256(f"{timestamp}\0{normalized}\0{args.kind}".encode()).hexdigest()[:16]

    for item in matching:
        if item.get("status") == "candidate" and promoted:
            item["status"] = "deprecated"
            item["updated_at"] = timestamp
            item["superseded_by"] = identifier

    record = {
        "id": identifier,
        "kind": args.kind,
        "summary": summary,
        "normalized": normalized,
        "scope": scope,
        "status": "promoted" if promoted else "candidate",
        "verified": verified,
        "confidence": confidence,
        "support_count": support,
        "run_id": clean_text(args.run_id, 120) if args.run_id else None,
        "evidence": evidence,
        "evidence_hashes": hashes,
        "evidence_fingerprint": fingerprint,
        "created_at": timestamp,
        "updated_at": timestamp,
        "feedback": [],
        "signature": "",
    }
    records.append(record)
    save_records(path, records)
    print(json.dumps({"stored": record, "memory": str(path)}, indent=2, ensure_ascii=True))


def search_command(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    path = memory_path(root)
    records = load_records(path)
    changed = reflect(root, records)
    if changed:
        save_records(path, records)
    allowed = {"promoted"}
    if args.include_candidates:
        allowed.add("candidate")
    scored = []
    for record in records:
        if record.get("status") not in allowed:
            continue
        score = similarity(args.query, str(record.get("summary", ""))) * float(record.get("confidence", 0.0))
        if score > 0.05:
            scored.append((score, record))
    scored.sort(key=lambda pair: (-pair[0], -float(pair[1].get("confidence", 0.0))))
    output = []
    for score, record in scored[: args.limit]:
        output.append({
            "id": record.get("id"),
            "kind": record.get("kind"),
            "summary": record.get("summary"),
            "scope": record.get("scope"),
            "confidence": record.get("confidence"),
            "support_count": record.get("support_count"),
            "relevance": round(score, 4),
            "evidence": record.get("evidence", []),
        })
    print(json.dumps({"memory": str(path), "results": output}, indent=2, ensure_ascii=True))


def feedback_command(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    path = memory_path(root)
    records = load_records(path)
    reflect(root, records)
    target = next((item for item in records if item.get("id") == args.id), None)
    if target is None:
        raise ValueError(f"memory record not found: {args.id}")
    event = {"outcome": args.outcome, "at": now()}
    if args.correction:
        event["correction"] = clean_text(args.correction, 800)
    target.setdefault("feedback", []).append(event)
    target["updated_at"] = event["at"]
    if args.outcome == "useful" and target.get("status") not in {"candidate", "promoted"}:
        raise ValueError(f"cannot mark {target.get('status')} lesson useful")
    if args.outcome == "useful" and target.get("verified"):
        target["useful_feedback_count"] = int(target.get("useful_feedback_count", 0)) + 1
    elif args.outcome in {"wrong", "stale"}:
        target["status"] = "deprecated" if args.outcome == "wrong" else "stale"
    elif args.outcome == "dead_end":
        target["status"] = "deprecated"
    replacement = None
    if args.outcome == "wrong" and args.correction:
        evidence = [clean_text(value, 300) for value in args.evidence]
        hashes = evidence_hashes(root, args.evidence)
        if args.verified and not hashes:
            raise ValueError("--verified correction requires an existing project-relative --evidence file")
        timestamp = now()
        summary = clean_text(args.correction, 800)
        replacement = {
            "id": hashlib.sha256(f"{timestamp}\0{normalize(summary)}\0correction".encode()).hexdigest()[:16],
            "kind": "correction",
            "summary": summary,
            "normalized": normalize(summary),
            "scope": target.get("scope", "project"),
            "status": "promoted" if args.verified else "candidate",
            "verified": bool(args.verified),
            "confidence": 0.9 if args.verified else 0.55,
            "support_count": 1,
            "run_id": clean_text(args.run_id, 120) if args.run_id else None,
            "evidence": evidence,
            "evidence_hashes": hashes,
            "evidence_fingerprint": evidence_fingerprint(hashes) if hashes else None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "feedback": [],
            "replaces": target.get("id"),
            "signature": "",
        }
        target["superseded_by"] = replacement["id"]
        records.append(replacement)
    save_records(path, records)
    print(json.dumps({"updated": target, "replacement": replacement}, indent=2, ensure_ascii=True))


def reflect_command(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    path = memory_path(root)
    records = load_records(path)
    changed = reflect(root, records)
    if changed:
        save_records(path, records)
    counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    print(json.dumps({"memory": str(path), "invalidated": changed, "status_counts": counts}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record", help="Store a thresholded lesson candidate")
    record_parser.add_argument("--root", default=".")
    record_parser.add_argument("--kind", choices=sorted(ALLOWED_KINDS), required=True)
    record_parser.add_argument("--summary", required=True)
    record_parser.add_argument("--scope", default="project")
    record_parser.add_argument("--evidence", action="append", default=[])
    record_parser.add_argument("--verified", action="store_true")
    record_parser.add_argument("--run-id", help="Stable identifier used to prove independent runs")
    record_parser.set_defaults(func=record_command)

    search_parser = subparsers.add_parser("search", help="Retrieve relevant promoted lessons")
    search_parser.add_argument("--root", default=".")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=3, choices=range(1, 11))
    search_parser.add_argument("--include-candidates", action="store_true")
    search_parser.set_defaults(func=search_command)

    feedback_parser = subparsers.add_parser("feedback", help="Record explicit lesson feedback")
    feedback_parser.add_argument("--root", default=".")
    feedback_parser.add_argument("--id", required=True)
    feedback_parser.add_argument("--outcome", choices=sorted(ALLOWED_FEEDBACK), required=True)
    feedback_parser.add_argument("--correction")
    feedback_parser.add_argument("--evidence", action="append", default=[])
    feedback_parser.add_argument("--verified", action="store_true")
    feedback_parser.add_argument("--run-id")
    feedback_parser.set_defaults(func=feedback_command)

    reflect_parser = subparsers.add_parser("reflect", help="Invalidate lessons with changed evidence")
    reflect_parser.add_argument("--root", default=".")
    reflect_parser.set_defaults(func=reflect_command)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
