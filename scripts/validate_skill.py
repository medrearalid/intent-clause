#!/usr/bin/env python3
"""Dependency-free structural validator for the IntentClause skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import NoReturn


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker == -1:
        fail("SKILL.md frontmatter is not closed")

    values: dict[str, str] = {}
    for line in text[4:marker].splitlines():
        if line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def validate_skill() -> None:
    if not SKILL.is_file():
        fail("SKILL.md is missing")

    text = SKILL.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        fail("frontmatter name is invalid")
    if ROOT.name != name:
        fail(f"skill directory '{ROOT.name}' must match name '{name}'")
    if not description or len(description) > 1024:
        fail("description must contain 1-1024 characters")
    if "Use ONLY" not in description or "Never activate automatically" not in description:
        fail("description must enforce explicit invocation")

    required_phrases = (
        "## Operating Modes and Gates",
        "## The Prompt Compiler Pipeline",
        "### Stage 6: Compile the Master Prompt",
        "### Stage 6.5: Route Model and Effort",
        "### Stage 7: Preflight and Execute",
        "### Stage 9: Learn Selectively",
        "## Failure Modes to Prevent",
    )
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"required section missing: {phrase}")

    for target in LINK_PATTERN.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        if not (ROOT / target).is_file():
            fail(f"broken local link: {target}")

    required_files = (
        "adapters/opencode/intent-clause.md",
        "adapters/opencode/ic.md",
        "adapters/claude/ic.md",
        "agents/openai.yaml",
        "references/context-routing.md",
        "references/learning-and-cache.md",
        "references/model-routing.md",
        "references/remote-intelligence.md",
        "scripts/context_router.py",
        "scripts/install.py",
        "scripts/memory.py",
        "tests/test_tools.py",
    )
    for relative in required_files:
        if not (ROOT / relative).is_file():
            fail(f"required resource missing: {relative}")

    for relative in ("adapters/opencode/intent-clause.md", "adapters/opencode/ic.md", "adapters/claude/ic.md"):
        command = (ROOT / relative).read_text(encoding="utf-8")
        if "$ARGUMENTS" not in command or "intent-clause" not in command:
            fail(f"command adapter does not forward arguments to the skill: {relative}")
    openai = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    if "allow_implicit_invocation: false" not in openai:
        fail("Codex manual invocation policy is missing")
    installer = (ROOT / "scripts/install.py").read_text(encoding="utf-8")
    if "disable-model-invocation: true" not in installer:
        fail("Claude installer does not inject the manual invocation guard")


def validate_evals() -> None:
    path = ROOT / "evals" / "cases.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid evals/cases.json: {exc}")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("evals/cases.json must contain at least one case")

    required = {"id", "input", "expected_mode", "expected_risk", "must", "must_not"}
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not required.issubset(case):
            fail(f"eval case {index} is missing required fields")
        if case["id"] in seen:
            fail(f"duplicate eval id: {case['id']}")
        seen.add(case["id"])
        if case["expected_mode"] not in {"EXECUTE", "PROMPT_ONLY", "PLAN_ONLY", "NOT_INVOKED"}:
            fail(f"invalid mode in eval {case['id']}")
        if case.get("expected_gate") not in {None, "CLARIFICATION_GATE", "MODEL_FIT_GATE", "APPROVAL_GATE"}:
            fail(f"invalid gate in eval {case['id']}")
        if case["expected_risk"] not in {"R0", "R1", "R2", "R3"}:
            fail(f"invalid risk in eval {case['id']}")
        if case.get("expected_context_tier") not in {None, "C0", "C1", "C2", "C3", "C4"}:
            fail(f"invalid context tier in eval {case['id']}")
        fixture = case.get("fixture_path")
        if fixture is not None and not (ROOT / fixture).is_dir():
            fail(f"missing fixture directory in eval {case['id']}: {fixture}")
        turns = case.get("turns", [])
        if not isinstance(turns, list):
            fail(f"turns must be a list in eval {case['id']}")
        for turn in turns:
            if not isinstance(turn, dict) or turn.get("role") != "user" or not turn.get("content"):
                fail(f"invalid follow-up turn in eval {case['id']}")
            if not isinstance(turn.get("must", []), list) or not isinstance(turn.get("must_not", []), list):
                fail(f"invalid turn rubric in eval {case['id']}")


def main() -> None:
    validate_skill()
    validate_evals()
    print("IntentClause skill validation passed")


if __name__ == "__main__":
    main()
