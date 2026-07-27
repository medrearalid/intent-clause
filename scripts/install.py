#!/usr/bin/env python3
"""Install IntentClause for a supported host with manual-invocation controls."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKIP_NAMES = {".git", ".intent-clause", "__pycache__"}
HOSTS = ("claude", "codex", "opencode")


def detect_host() -> str:
    home = Path.home()
    markers = {
        "claude": home / ".claude",
        "codex": home / ".agents",
        "opencode": home / ".config" / "opencode",
    }
    detected = [host for host, marker in markers.items() if marker.is_dir()]
    if len(detected) == 1:
        return detected[0]
    if not detected:
        raise ValueError(f"host could not be detected; choose one of: {', '.join(HOSTS)}")
    raise ValueError(
        f"multiple hosts detected ({', '.join(detected)}); specify one explicitly"
    )


def destinations(host: str, scope: str, project: Path) -> tuple[Path, list[Path]]:
    if scope == "project":
        bases = {
            "claude": project / ".claude" / "skills",
            "codex": project / ".agents" / "skills",
            "opencode": project / ".opencode" / "skills",
        }
        command_bases = {
            "claude": project / ".claude" / "commands",
            "opencode": project / ".opencode" / "commands",
        }
    else:
        home = Path.home()
        bases = {
            "claude": home / ".claude" / "skills",
            "codex": home / ".agents" / "skills",
            "opencode": home / ".config" / "opencode" / "skills",
        }
        command_bases = {
            "claude": home / ".claude" / "commands",
            "opencode": home / ".config" / "opencode" / "commands",
        }

    commands: list[Path] = []
    if host == "opencode":
        commands = [command_bases[host] / "intent-clause.md", command_bases[host] / "ic.md"]
    elif host == "claude":
        commands = [command_bases[host] / "ic.md"]
    return bases[host] / "intent-clause", commands


def ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in SKIP_NAMES or name.endswith((".pyc", ".pyo"))}


def ensure_contained(root: Path, target: Path) -> None:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"installation root is not a directory: {root}")
    try:
        relative = target.absolute().relative_to(root)
    except ValueError as exc:
        raise ValueError(f"installation target escapes its root: {target}") from exc

    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"installation path contains a redirect: {current}")
        if not current.exists():
            continue
        if not current.resolve().is_relative_to(root):
            raise ValueError(f"installation path contains a redirect: {current}")


def inject_claude_guard(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    if "disable-model-invocation:" in text.split("\n---\n", 1)[0]:
        return
    marker = "compatibility:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(marker):
            lines.insert(index + 1, "disable-model-invocation: true")
            skill_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError("SKILL.md compatibility field not found; cannot inject Claude guard")


def install(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    target, command_targets = destinations(args.host, args.scope, project)

    if target.is_relative_to(ROOT):
        raise ValueError("installation target cannot be inside the IntentClause source directory")
    containment_root = project if args.scope == "project" else Path.home().resolve()
    ensure_contained(containment_root, target)
    for command_target in command_targets:
        ensure_contained(containment_root, command_target)

    if args.dry_run:
        print(f"skill: {target}")
        for command_target in command_targets:
            print(f"command: {command_target}")
        print(f"claude_guard: {args.host == 'claude'}")
        return

    if target.exists():
        if target.is_symlink():
            raise ValueError(f"refusing redirected installation target: {target}")
        if not args.force:
            raise FileExistsError(f"target exists: {target}; use --force to replace it")
    for command_target in command_targets:
        if command_target.exists() and not args.force:
            raise FileExistsError(f"command exists: {command_target}; use --force to replace it")

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, target, ignore=ignore)

    if args.host == "claude":
        inject_claude_guard(target / "SKILL.md")
    for command_target in command_targets:
        command_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "adapters" / args.host / command_target.name, command_target)

    print(f"Installed IntentClause skill: {target}")
    for command_target in command_targets:
        print(f"Installed /{command_target.stem} command: {command_target}")
    if args.host in {"codex", "opencode"}:
        print("Restart the host if it does not detect the new skill or command.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", nargs="?", choices=HOSTS, help="Host to install for (auto-detected when omitted)")
    parser.add_argument("--host", dest="legacy_host", choices=HOSTS, help=argparse.SUPPRESS)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", default=".", help="Project root for --scope project")
    parser.add_argument("--force", action="store_true", help="Replace an existing installation")
    parser.add_argument("--dry-run", action="store_true", help="Show destinations without writing")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.host and args.legacy_host:
        parser.error("host must be supplied either positionally or with --host, not both")
    args.host = args.host or args.legacy_host
    try:
        args.host = args.host or detect_host()
        install(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
