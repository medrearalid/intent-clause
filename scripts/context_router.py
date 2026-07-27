#!/usr/bin/env python3
"""Build a token-budgeted project context plan without reading file bodies."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_BUDGET = 2000
DEFAULT_MAX_FILES = 8
MODULE_MANIFEST = Path(__file__).resolve().parent.parent / "modules.json"
MAX_INVENTORY_FILES = 50_000
MAX_FILE_BYTES = 1_000_000
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}")
STOP_WORDS = {
    "about", "after", "again", "also", "and", "before", "build", "create",
    "from", "into", "make", "project", "prompt", "simple", "that", "the",
    "this", "use", "using", "with", "icin", "bir", "bunu", "bunun", "ve",
}
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".next", ".nuxt", ".output",
    ".intent-clause", "__pycache__", "build", "coverage", "dist", "node_modules",
    "target", "vendor", "venv", ".venv",
}
SENSITIVE_PARTS = {
    ".env", ".env.local", ".env.production", "credentials", "id_rsa", "id_ed25519",
    "private-key", "secrets", "secrets.json",
}
PRIORITY_NAMES = {
    "agents.md": 100,
    "claude.md": 100,
    "readme.md": 80,
    "package.json": 75,
    "pyproject.toml": 75,
    "cargo.toml": 75,
    "go.mod": 75,
    "pom.xml": 75,
    "build.gradle": 75,
    "build.gradle.kts": 75,
    "composer.json": 75,
    "gemfile": 75,
    "requirements.txt": 70,
    "tsconfig.json": 65,
    "docker-compose.yml": 60,
    "docker-compose.yaml": 60,
    "dockerfile": 55,
    "makefile": 55,
}


@dataclass
class Candidate:
    path: str
    size: int
    score: int = 0
    reasons: set[str] = field(default_factory=set)

    @property
    def estimated_tokens(self) -> int:
        return max(1, 64 + (self.size + 1) // 2)

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "size_bytes": self.size,
            "estimated_tokens": self.estimated_tokens,
            "read_strategy": "search-then-slice" if self.size > 16_000 else "bounded-read",
            "score": self.score,
            "reasons": sorted(self.reasons),
        }


def query_terms(query: str) -> set[str]:
    terms = {match.group(0).lower() for match in TOKEN_PATTERN.finditer(query)}
    return {term for term in terms if len(term) >= 3 and term not in STOP_WORDS}


def run_git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, result.stdout.strip()


def is_sensitive(relative_path: str) -> bool:
    parts = {part.lower() for part in Path(relative_path).parts}
    name = Path(relative_path).name.lower()
    return name in SENSITIVE_PARTS or bool(parts & SENSITIVE_PARTS) or name.endswith((".pem", ".key", ".p12", ".pfx"))


def safe_project_file(root: Path, path: Path) -> bool:
    try:
        relative = path.absolute().relative_to(root.resolve())
    except ValueError:
        return False
    current = root.resolve()
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return False
    try:
        return path.is_file() and path.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def inventory(root: Path, is_git: bool) -> tuple[list[str], bool]:
    if is_git:
        ok, output = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
        if ok:
            paths = [line.replace("\\", "/") for line in output.splitlines() if line]
            return paths[:MAX_INVENTORY_FILES], len(paths) > MAX_INVENTORY_FILES

    paths: list[str] = []
    truncated = False
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        current_path = Path(current)
        for name in files:
            try:
                relative = (current_path / name).relative_to(root).as_posix()
            except ValueError:
                continue
            paths.append(relative)
            if len(paths) >= MAX_INVENTORY_FILES:
                truncated = True
                return paths, truncated
    return paths, truncated


def git_context(root: Path, is_git: bool) -> dict[str, object]:
    if not is_git:
        return {"is_repository": False}

    _, branch = run_git(root, "branch", "--show-current")
    _, status = run_git(root, "status", "--short")
    _, commits = run_git(root, "log", "--oneline", "-8")
    changed = []
    for line in status.splitlines():
        path = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not is_sensitive(path):
            changed.append(path.replace("\\", "/")[:240])
    return {
        "is_repository": True,
        "branch": branch or None,
        "changed_paths": changed[:50],
        "recent_commits": [line[:160] for line in commits.splitlines()[:8]],
    }


def rank_candidates(root: Path, paths: list[str], terms: set[str], changed: set[str]) -> tuple[list[Candidate], int]:
    candidates: list[Candidate] = []
    total_bytes = 0
    for relative in paths:
        if is_sensitive(relative):
            continue
        path = root / relative
        try:
            if not safe_project_file(root, path):
                continue
            size = path.stat().st_size
        except OSError:
            continue
        total_bytes += size
        if size > MAX_FILE_BYTES:
            continue

        lowered = relative.lower()
        name = path.name.lower()
        score = 0
        reasons: set[str] = set()
        parts = Path(relative).parts
        is_instruction = name in {"agents.md", "claude.md"}
        if name in PRIORITY_NAMES and (len(parts) == 1 or is_instruction):
            score += PRIORITY_NAMES[name]
            reasons.add("project-skeleton")
        if relative in changed:
            score += 90
            reasons.add("git-changed")
        matches = sorted(term for term in terms if term in lowered)
        if matches:
            score += min(70, 18 * len(matches))
            reasons.add("query-term:" + ",".join(matches[:4]))
        if any(segment in lowered for segment in ("test", "spec")) and matches:
            score += 15
            reasons.add("related-test")
        if score > 0:
            candidates.append(Candidate(relative, size, score, reasons))

    candidates.sort(key=lambda item: (-item.score, item.estimated_tokens, item.path))
    return candidates, total_bytes


def select_budgeted(candidates: list[Candidate], budget: int, max_files: int) -> tuple[list[Candidate], int]:
    selected: list[Candidate] = []
    used = 0
    for candidate in candidates:
        if len(selected) >= max_files:
            break
        cost = candidate.estimated_tokens
        if selected and used + cost > budget:
            continue
        if not selected and cost > budget:
            continue
        selected.append(candidate)
        used += cost
    return selected, used


def metadata_token_estimate(git: dict[str, object], terms: set[str]) -> int:
    payload = {"query_terms": sorted(terms), "git": git}
    return 64 + (len(json.dumps(payload, ensure_ascii=True)) + 1) // 2


def fit_query_terms(terms: set[str], limit: int) -> tuple[set[str], bool]:
    fitted: set[str] = set()
    for term in sorted(terms, key=lambda value: (len(value), value)):
        proposal = fitted | {term}
        if metadata_token_estimate({"is_repository": False}, proposal) > limit:
            break
        fitted = proposal
    return fitted, len(fitted) < len(terms)


def fit_git_metadata(git: dict[str, object], terms: set[str], limit: int) -> tuple[dict[str, object], int]:
    fitted: dict[str, object] = {"is_repository": bool(git.get("is_repository"))}
    if not fitted["is_repository"]:
        return fitted, metadata_token_estimate(fitted, terms)

    branch = git.get("branch")
    if branch:
        proposal = {**fitted, "branch": str(branch)[:80]}
        if metadata_token_estimate(proposal, terms) <= limit:
            fitted = proposal

    for key in ("changed_paths", "recent_commits"):
        values = git.get(key, [])
        if not isinstance(values, list):
            continue
        accepted: list[str] = []
        for value in values:
            proposal_values = accepted + [str(value)]
            proposal = {**fitted, key: proposal_values}
            if metadata_token_estimate(proposal, terms) > limit:
                break
            accepted = proposal_values
        if accepted:
            fitted[key] = accepted
    return fitted, metadata_token_estimate(fitted, terms)


def route(query: str, file_count: int, graph_exists: bool, is_git: bool, truncated: bool) -> str:
    lowered = query.lower()
    architecture_terms = ("architecture", "dependency", "flow", "relationship", "calls", "mimari", "bagim", "akis")
    history_terms = ("regression", "recent", "commit", "changed", "history", "why", "regresyon", "neden", "degis")
    if graph_exists and (file_count > 500 or any(term in lowered for term in architecture_terms)):
        return "graphify-query"
    if is_git and any(term in lowered for term in history_terms):
        return "git-first"
    if truncated or file_count > 5_000:
        return "focused-search-or-index"
    return "focused-read"


def module_plan(query: str) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    manifest = json.loads(MODULE_MANIFEST.read_text(encoding="utf-8"))["modules"]
    lowered = query.lower()
    selected: dict[str, str] = {
        "context-routing": "project evidence is required",
    }

    signals = {
        "prompt-compiler": ("architecture", "cross-file", "complex", "migration", "mimari", "katman"),
        "model-routing": ("architecture", "security", "migration", "mimari", "model recommendation"),
        "execution": ("implement", "refactor", "fix", "change", "update", "add", "uygula", "duzelt"),
        "optimization": ("optimiz", "performance", "faster", "speed", "token", "cost", "latency", "hiz"),
        "safety": ("auth", "permission", "secret", "security", "privacy", "production", "migration", "guven"),
        "remote": ("--remote",),
        "domain-frontend": ("frontend", "react", "css", "ui", "ux", "design", "tasarim"),
        "domain-data": ("analytics", "dataset", "machine learning", "model training", "veri"),
        "domain-devops": ("deploy", "cloud", "docker", "kubernetes", "database", "devops", "migration"),
        "domain-security": ("security", "privacy", "auth", "permission", "threat", "guvenlik"),
        "domain-research": ("research", "documentation", "write", "citation", "arastir", "dokuman"),
        "domain-business": ("marketing", "conversion", "business", "funnel", "product strategy", "pazarlama"),
    }
    for module, terms in signals.items():
        matched = next((term for term in terms if term in lowered), None)
        if matched:
            selected[module] = f"request signal: {matched}"

    if not any(name.startswith("domain-") for name in selected):
        selected["domain-software"] = "default project engineering domain"

    modules = [
        {
            "id": name,
            "path": manifest[name]["path"],
            "reason": reason,
            "required": True,
            "estimated_tokens": manifest[name]["estimated_tokens"],
        }
        for name, reason in selected.items()
    ]
    excluded = [
        {"id": name, "reason": f"trigger absent: {config['load_when']}"}
        for name, config in manifest.items()
        if name not in selected
    ]
    return modules, excluded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--query", required=True, help="Sanitized user request")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="Evidence token budget")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES, help="Maximum candidate files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Project root is not a directory: {root}"}))
        raise SystemExit(2)
    if args.budget < 256 or args.budget > 20_000:
        print(json.dumps({"error": "Budget must be between 256 and 20000 tokens"}))
        raise SystemExit(2)
    if args.max_files < 1 or args.max_files > 100:
        print(json.dumps({"error": "max-files must be between 1 and 100"}))
        raise SystemExit(2)

    git_ok, _ = run_git(root, "rev-parse", "--is-inside-work-tree")
    paths, truncated = inventory(root, git_ok)
    raw_git = git_context(root, git_ok)
    metadata_limit = min(1000, max(256, args.budget // 4))
    raw_terms = query_terms(args.query)
    terms, terms_truncated = fit_query_terms(raw_terms, metadata_limit)
    git, metadata_tokens = fit_git_metadata(raw_git, terms, metadata_limit)
    changed_paths = raw_git.get("changed_paths", [])
    changed = set(changed_paths) if isinstance(changed_paths, list) else set()
    candidates, total_bytes = rank_candidates(root, paths, terms, changed)
    selected, file_tokens = select_budgeted(candidates, max(0, args.budget - metadata_tokens), args.max_files)
    used = metadata_tokens + file_tokens
    graph_path = root / "graphify-out" / "graph.json"
    graph_available = safe_project_file(root, graph_path)
    memory_path = root / ".intent-clause" / "memory.jsonl"
    memory_available = safe_project_file(root, memory_path)
    modules, excluded_modules = module_plan(args.query)

    output = {
        "project_root": str(root),
        "query_terms": sorted(terms),
        "query_terms_truncated": terms_truncated,
        "budget": {
            "planning_limit_tokens": args.budget,
            "metadata_estimated_tokens": metadata_tokens,
            "file_estimated_tokens": file_tokens,
            "planned_tokens": used,
            "remaining_tokens": args.budget - used,
            "enforcement_scope": "router evidence plan only; host-retained tool output is outside this estimate",
        },
        "project_scale": {
            "inventoried_files": len(paths),
            "inventory_truncated": truncated,
            "estimated_total_bytes": total_bytes,
        },
        "indexes": {
            "graphify_graph": str(graph_path) if graph_available else None,
            "intent_clause_memory": str(memory_path) if memory_available else None,
        },
        "git": git,
        "recommended_route": route(args.query, len(paths), graph_available, git_ok, truncated),
        "modules": modules,
        "excluded_modules": excluded_modules,
        "candidates": [candidate.as_dict() for candidate in selected],
        "notes": [
            "No candidate file bodies were read.",
            "Verify consequential graph or memory claims at current source locations.",
            "Escalate the budget only for a named unresolved decision.",
        ],
    }
    print(json.dumps(output, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
