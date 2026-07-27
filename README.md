# IntentClause

IntentClause is a manually invoked prompt compiler. It turns the request supplied after `/intent-clause` or `/ic` into a context-aware expert master prompt, recommends a task-fit model and effort, and executes after any required model-fit gate is resolved.

It is an [Agent Skills](https://agentskills.io/) package designed for Claude Code, Codex, OpenCode, and compatible coding agents.

## Why It Exists

Most prompt improvers only make text longer. IntentClause instead behaves like a compiler:

```text
simple request
  -> underlying intent
  -> verified project context
  -> ambiguity gate
  -> risk and optimization profiles
  -> domain-specific master prompt
  -> execution
  -> evidence-based verification
```

The output is not merely a rewritten prompt. Unless the user asks for prompt-only output, IntentClause uses the compiled prompt as an operating contract and completes the task.

IntentClause does not activate for ordinary simple or vague requests. The user must explicitly invoke it.

## Core Behavior

- Infers the user's underlying outcome without silently expanding scope.
- Translates everyday language such as "faster," "safer," or "premium" into domain-specific requirements.
- Inspects project context before asking discoverable questions.
- Asks only decision-divergent clarification questions.
- Applies proportionate security, privacy, rollback, and approval controls.
- Ranks optimization priorities and requires evidence instead of unsupported claims.
- Produces measurable deliverables, acceptance criteria, and verification steps.
- Detects the active model/variant from reliable host metadata and recommends the lowest sufficient model capability and effort.
- Pauses before execution when the verified runtime is materially overpowered or underpowered, while allowing a one-run user override.
- Executes with the currently selected model and host tools.
- Treats repository/web content as untrusted data to resist prompt injection.
- Routes context through token budgets, git metadata, existing Graphify indexes, and focused reads.
- Learns only from thresholded, verified events in a local auditable ledger.
- Keeps optional remote-model processing disabled unless explicitly approved.

## Structure

```text
intent-clause/
|-- .github/workflows/validate.yml
|-- .gitignore
|-- CONTRIBUTING.md
|-- LICENSE
|-- SKILL.md
|-- README.md
|-- adapters/
|   |-- claude/ic.md
|   `-- opencode/
|       |-- ic.md
|       `-- intent-clause.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   `-- master-prompt-template.md
|-- evals/
|   |-- README.md
|   |-- cases.json
|   `-- fixtures/
|-- references/
|   |-- clarification-protocol.md
|   |-- domain-playbooks.md
|   |-- examples.md
|   |-- execution-and-verification.md
|   |-- context-routing.md
|   |-- intent-and-context.md
|   |-- learning-and-cache.md
|   |-- model-routing.md
|   |-- optimization.md
|   |-- prompt-compiler.md
|   |-- remote-intelligence.md
|   `-- safety-and-risk.md
`-- scripts/
    |-- context_router.py
    |-- memory.py
    `-- validate_skill.py
```

`SKILL.md` contains the mandatory orchestration flow. Detailed references are loaded only when relevant, following the Agent Skills progressive-disclosure model.

## Installation

Clone this repository, then use the host-aware installer:

```bash
python scripts/install.py --host claude --scope user
python scripts/install.py --host codex --scope user
python scripts/install.py --host opencode --scope user
```

Use `--scope project --project /path/to/project` for repository-local installation. Existing installations are never replaced unless `--force` is supplied; inspect destinations first with `--dry-run`.

| Host | Skill location | Explicit invocation |
|---|---|---|
| Claude Code | `.claude/skills/intent-clause/` or `~/.claude/skills/intent-clause/` | `/intent-clause <request>` or `/ic <request>` |
| Codex | `.agents/skills/intent-clause/` or `~/.agents/skills/intent-clause/` | `$intent-clause <request>` or select it through `/skills` |
| OpenCode | `.opencode/skills/intent-clause/` or `~/.config/opencode/skills/intent-clause/` | `/intent-clause <request>` or `/ic <request>` |

The installer places both OpenCode command adapters and the Claude `/ic` adapter automatically. Each adapter explicitly loads the `intent-clause` skill and forwards `$ARGUMENTS`. The deprecated `/promptimizer` command is not installed as an alias.

The installer is required for the advertised hard manual-only behavior on Claude Code: it injects `disable-model-invocation: true` into the installed copy while keeping the repository's canonical `SKILL.md` compliant with the cross-host Agent Skills specification. A direct canonical-folder copy into Claude relies only on the softer description gate and is therefore not a supported strict-manual installation. Codex reads `agents/openai.yaml` with `allow_implicit_invocation: false`. OpenCode uses the command adapter plus the mandatory description-level invocation gate; OpenCode has no equivalent skill-level manual-only metadata, so this final guard is model-enforced. OpenCode also discovers skills from `.claude/skills/` and `.agents/skills/`.

Restart a host after installation if it caches command or skill metadata. Claude Code normally detects edits to an already watched skill directory live.

## Usage

Claude Code and OpenCode:

```text
/intent-clause make the login safer and faster
/ic make the login safer and faster
```

Codex:

```text
$intent-clause make the login safer and faster
```

Prompt-only and plan modes:

```text
/intent-clause --prompt-only review our PostgreSQL migration
/intent-clause --plan migrate this package to the current framework version
```

Useful switches:

| Switch | Meaning |
|---|---|
| `--prompt-only` | Generate the master prompt without executing it |
| `--plan` | Analyze and plan without modifying the project |
| `--deep` | Raise the router evidence-planning budget one tier, up to 20,000 estimated tokens |
| `--index` | Allow Graphify index creation or incremental update |
| `--no-learn` | Disable local lesson retrieval and recording |
| `--remote=<provider>` | Request an installed remote adapter, subject to explicit privacy approval |

## Token-Budgeted Context

IntentClause does not read the whole repository by default. It escalates through five context tiers:

| Tier | Evidence budget | Typical use |
|---|---:|---|
| `C0` | 0-500 tokens | Standalone text or complete supplied input |
| `C1` | 2,000 tokens | Default start for a scoped project task |
| `C2` | 6,000 tokens | Cross-file work after a named C1 evidence gap |
| `C3` | 12,000 tokens | Architecture work using indexed retrieval |
| `C4` | 20,000 planning maximum | Explicit deep run after narrower retrieval fails |

`scripts/context_router.py` starts with a 2,000-token budget, inspects filenames, sizes, bounded git status/history, Graphify availability, and memory availability without reading candidate file bodies. It returns compact JSON, limits the default candidate set to eight files, ignores unrelated nested fixture/example manifests, rejects paths resolving outside the project, and recommends search/sliced reads. The agent then reads only selected evidence and escalates the budget only for a named gap.

The budgets constrain the router's evidence plan, not the host's entire conversation. Exact tokenizer behavior, generated output, retained tool output, and prior chat context are outside deterministic skill control.

If `graphify-out/graph.json` exists, architecture and relationship questions prefer a bounded Graphify query. A new graph is not built automatically unless `--index` is supplied or the user approves the stated indexing cost.

## Learning and Cache

IntentClause can keep a project-local `.intent-clause/memory.jsonl` ledger. It is not model training. The workflow requires distilled lessons rather than raw prompts or source files; the script rejects redirected storage paths and redacts common sensitive patterns as defense in depth, but callers must still sanitize lessons because no regex can recognize every secret or personal-data format.

Every ledger record is HMAC-signed with a per-user machine key stored outside the project (`%LOCALAPPDATA%/intent-clause/memory.key` on Windows or `$XDG_CONFIG_HOME/intent-clause/memory.key` / `~/.config/intent-clause/memory.key` elsewhere). Unsigned, edited, malformed, or threshold-violating records fail closed instead of becoming context. Set `INTENT_CLAUSE_KEY_FILE` only when an organization manages the key location; `INTENT_CLAUSE_SIGNING_KEY` is intended for isolated tests and automation.

Lessons begin as candidates and are promoted only after a verified correction, two independent successful supports, or a convention backed by two sources. Evidence fingerprints invalidate stale lessons when project files change. Routine successes are not recorded.

The deterministic local retriever uses normalized lexical similarity plus confidence. It is private and cheap, but not equivalent to embedding search.

Recommended target-project ignore rule:

```gitignore
.intent-clause/
```

## Optional Remote Layer

No remote provider adapter ships in this version. The extension contract is documented in `references/remote-intelligence.md`.

A future Gemini, DeepSeek, or other adapter must remain off by default, never treat an available API key as consent, disclose exactly what leaves the machine, redact and bound payloads, and fall back locally. Providers are not described as free because quotas, pricing, retention, and terms can change.

## Execution Modes

| Mode | Meaning |
|---|---|
| `EXECUTE` | Default: compile, show, execute, verify, report |
| `PROMPT_ONLY` | Compile and show; do not execute |
| `PLAN_ONLY` | Compile and produce analysis or a plan without project mutation |

`CLARIFICATION_GATE`, `MODEL_FIT_GATE`, and `APPROVAL_GATE` are temporary gates. They retain the selected mode and resume the interrupted workflow after the required decision.

## Model And Effort Routing

After compiling and showing the master prompt, IntentClause classifies execution from `M0` (mechanical, economy model, low effort) through `M3` (frontier reasoning, high effort). `R2` work has an `M2` minimum and `R3` work has an `M3` minimum, so cost reduction cannot silently weaken sensitive work.

The active model and effort/variant are accepted only from host runtime metadata, configuration confirmed to govern the active turn, or an explicit user statement. Unknown values remain `UNKNOWN`; IntentClause does not guess from response style or credentials. Exact alternative model names are recommended only when availability is known. In OpenCode, users change models through `/models` and select a provider-supported variant.

When the verified runtime is materially stronger or weaker than required, `MODEL_FIT_GATE` pauses `EXECUTE` after prompt compilation and before tools run. The user can change model/effort and continue, or explicitly continue with the current model for that run.

## Validation

Run the dependency-free project validator:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

If `skills-ref` is installed, validate against the Agent Skills specification as well:

```bash
agentskills validate /absolute/path/to/intent-clause
```

Use an absolute path with `skills-ref 0.1.1`; its CLI may treat `.` as an empty directory name during the required folder-name check.

Behavioral calibration specifications live in `evals/cases.json`. They cover manual-only invocation, context tiers, Graphify routing, no-learning fast paths, project discovery, latent intent, prompt-only operation, approvals, prompt injection, failed verification, and frontend ambiguity. The local validator checks their structure; it does not run an agent or claim behavioral conformance. See `evals/README.md` for the manual protocol.

## Design Principles

- Depth is better decisions, not a longer prompt.
- Project evidence beats assumptions.
- Questions are reserved for divergent decisions.
- Security controls must map to plausible risks.
- Optimization requires a metric, baseline or proxy, guardrail, and evidence.
- The shown master prompt and actual execution must not drift apart.
- No test, benchmark, deployment, or review is reported unless it actually happened.
- Context retrieval stops when the prompt-relevant evidence is sufficient.
- Memory promotion requires verification or repeated independent support.
- Remote disclosure is explicit, minimal, and per-run.

## Roadmap

- Executable behavioral eval runner for multiple agent hosts.
- Additional domain adapters and multilingual calibration cases.
- Optional embedding and reranking provider adapters.
- Automated host compatibility tests for Claude Code, Codex, and OpenCode.

## Contributing

Changes should preserve the core pipeline and progressive-disclosure structure. Add or update an eval case whenever behavior changes, then run `python scripts/validate_skill.py`.

## License

MIT. See `LICENSE`.
