# IntentClause

> A manually invoked prompt compiler that turns a short request into a context-aware, executable operating contract.

[![Validate skill](https://github.com/medrearalid/intent-clause/actions/workflows/validate.yml/badge.svg)](https://github.com/medrearalid/intent-clause/actions/workflows/validate.yml)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827)](https://agentskills.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563eb.svg)](LICENSE)

IntentClause is an [Agent Skills](https://agentskills.io/) package for Claude Code, Codex, OpenCode, and compatible coding agents. It inspects only the context a task needs, compiles a precise master prompt, recommends a task-fit model and effort, and then executes with evidence-based verification.

It does not activate automatically. Invoke it explicitly with `/intent-clause`, `/ic`, or `$intent-clause`.

[Quick start](#quick-start) | [How it works](#how-it-works) | [Installation](#installation) | [Usage](#usage) | [Validation](#validation)

## Why IntentClause?

Most prompt improvers make a request longer. IntentClause makes it operational:

```text
simple request
  -> underlying intent
  -> verified project context
  -> ambiguity and risk gates
  -> task-fit master prompt
  -> execution
  -> evidence-based verification
```

The result is not merely rewritten text. Unless you select prompt-only or plan mode, the compiled prompt becomes the contract IntentClause follows to complete the task.

### What it adds

| Capability | What it does |
|---|---|
| Intent decoding | Converts terms such as "faster," "safer," or "premium" into domain-specific requirements. |
| Focused context | Uses token budgets, git metadata, existing Graphify indexes, and bounded file reads instead of scanning the repository. |
| Selective policy loading | Produces an explainable module plan and loads only the domain and control references triggered by the task. |
| Minimal clarification | Asks only questions whose answers would materially change the implementation. |
| Proportionate safeguards | Adds security, privacy, rollback, and approval controls only when the task requires them. |
| Model routing | Recommends the lowest sufficient model capability and effort without claiming to switch the active model. |
| Verifiable execution | Defines acceptance criteria and reports only checks that actually ran. |
| Private local learning | Stores only thresholded, signed, evidence-backed lessons in a project-local ledger. |
| Prompt-injection resistance | Treats repository and web content as untrusted evidence rather than instructions. |

## Quick Start

Clone the repository and install IntentClause. If only one supported host is configured, it is detected automatically:

```bash
git clone https://github.com/medrearalid/intent-clause.git
cd intent-clause

python scripts/install.py
# If multiple hosts are configured: python scripts/install.py opencode
```

Restart the host if it caches commands or skill metadata, then invoke IntentClause:

```text
/ic make the login safer and faster
```

IntentClause will:

1. Interpret the underlying outcome.
2. Inspect the minimum useful project context.
3. Resolve only blocking ambiguities.
4. Show the compiled master prompt and model recommendation.
5. Execute, verify, and report the result.

## How It Works

IntentClause follows a progressive pipeline designed to increase precision without silently increasing scope.

| Stage | Purpose |
|---|---|
| 1. Decode intent | Identify the real outcome, audience, constraints, and success signals. |
| 2. Route context | Start with a small evidence budget and inspect only relevant project surfaces. |
| 3. Resolve ambiguity | Pause only when an unresolved decision would produce meaningfully different results. |
| 4. Profile risk | Match safeguards and approval requirements to the task's actual impact. |
| 5. Compile | Produce a self-contained master prompt with deliverables and acceptance criteria. |
| 6. Route model | Classify task complexity and recommend the lowest sufficient capability and effort. |
| 7. Execute | Use the compiled prompt as the operating contract. |
| 8. Verify and learn | Report real evidence and retain a lesson only when strict thresholds are met. |

Three temporary gates can pause execution without discarding progress:

| Gate | Trigger |
|---|---|
| `CLARIFICATION_GATE` | A decision-divergent unknown cannot be resolved from project evidence. |
| `MODEL_FIT_GATE` | The verified runtime is materially stronger or weaker than the task requires. |
| `APPROVAL_GATE` | The next action is destructive, privileged, costly, external, or irreversible. |

## Installation

The host-aware installer checks destinations before writing and never replaces an existing installation unless `--force` is supplied.

```bash
python scripts/install.py [host]
```

| Host | Skill location | Invocation |
|---|---|---|
| Claude Code | `.claude/skills/intent-clause/` or `~/.claude/skills/intent-clause/` | `/intent-clause <request>` or `/ic <request>` |
| Codex | `.agents/skills/intent-clause/` or `~/.agents/skills/intent-clause/` | `$intent-clause <request>` or select it through `/skills` |
| OpenCode | `.opencode/skills/intent-clause/` or `~/.config/opencode/skills/intent-clause/` | `/intent-clause <request>` or `/ic <request>` |

Use project scope when you want a repository-local installation:

```bash
python scripts/install.py opencode --scope project --project /path/to/project
```

Preview changes before installation:

```bash
python scripts/install.py claude --dry-run
```

The previous `--host <host>` form remains supported for existing scripts.

When the host argument is omitted, the installer uses the single detected Claude Code, Codex, or OpenCode configuration. It asks for an explicit host instead of guessing when none or several are detected.

<details>
<summary><strong>Manual-invocation behavior by host</strong></summary>

The installer is required for strict manual-only behavior on Claude Code. It injects `disable-model-invocation: true` into the installed copy while keeping the canonical repository `SKILL.md` compatible with the cross-host Agent Skills specification. A direct canonical-folder copy into Claude relies only on the softer description gate and is not a supported strict-manual installation.

Codex reads `agents/openai.yaml` with `allow_implicit_invocation: false`. OpenCode uses the command adapter and mandatory description-level invocation gate; OpenCode does not provide an equivalent skill-level manual-only metadata field, so its final guard is model-enforced. OpenCode also discovers skills from `.claude/skills/` and `.agents/skills/`.

The installer adds both OpenCode command adapters and the Claude `/ic` adapter. The deprecated `/promptimizer` command is not installed as an alias.

</details>

## Usage

### Standard execution

Claude Code and OpenCode:

```text
/intent-clause make the login safer and faster
/ic make the login safer and faster
```

Codex:

```text
$intent-clause make the login safer and faster
```

### Prompt-only and plan modes

```text
/intent-clause --prompt-only review our PostgreSQL migration
/intent-clause --plan migrate this package to the current framework version
```

| Switch | Effect |
|---|---|
| `--prompt-only` | Generate and show the master prompt without executing it. |
| `--plan` | Analyze and plan without modifying the project. |
| `--deep` | Raise the router evidence-planning budget one tier, up to 20,000 estimated tokens. |
| `--index` | Allow Graphify index creation or an incremental update. |
| `--no-learn` | Disable local lesson retrieval and recording for the run. |
| `--remote=<provider>` | Request an installed remote adapter, subject to explicit privacy approval. |

### Execution modes

| Mode | Behavior |
|---|---|
| `EXECUTE` | Default: compile, show, execute, verify, and report. |
| `PROMPT_ONLY` | Compile and show; do not execute. |
| `PLAN_ONLY` | Compile and produce analysis or a plan without project mutation. |

## Context, Privacy, and Learning

### Token-budgeted context

IntentClause starts small and escalates only after identifying a concrete evidence gap.

| Tier | Evidence budget | Typical use |
|---|---:|---|
| `C0` | 0-500 tokens | Standalone text or complete supplied input. |
| `C1` | 2,000 tokens | Default starting point for a scoped project task. |
| `C2` | 6,000 tokens | Cross-file work after a named C1 evidence gap. |
| `C3` | 12,000 tokens | Architecture work using indexed retrieval. |
| `C4` | 20,000-token planning ceiling | Explicit deep run after narrower retrieval fails. |

`scripts/context_router.py` inventories filenames, sizes, bounded git status and history, Graphify availability, and memory availability without reading candidate file bodies. It returns compact JSON, limits the default candidate set to eight files, ignores unrelated nested fixture or example manifests, rejects paths resolving outside the project, and recommends focused searches or sliced reads.

The router also reads `modules.json` and emits `modules` and `excluded_modules`. Every selected module includes its path, estimated token cost, and selection reason. Security, remote, learning, optimization, and domain guidance therefore remain unloaded until their trigger is present. Runtime rules in `SKILL.md` remain authoritative when a heuristic signal is incomplete.

These budgets constrain the router's evidence plan, not the host's entire conversation. Generated output, retained tool output, prior conversation history, and tokenizer variance remain outside deterministic skill control.

If `graphify-out/graph.json` exists, architecture and relationship requests prefer a bounded Graphify query. IntentClause does not build a new graph unless `--index` is supplied or the user approves the stated indexing cost.

### Local learning

IntentClause can store project-scoped lessons in `.intent-clause/memory.jsonl`. This is an auditable local ledger, not model training.

- Records contain distilled lessons rather than raw prompts or source files.
- Common sensitive patterns are redacted as defense in depth, but callers must still sanitize lessons.
- Every record is HMAC-signed with a per-user machine key stored outside the project.
- Unsigned, edited, malformed, redirected, or threshold-violating records fail closed.
- Evidence fingerprints invalidate lessons when supporting project files change.
- Routine successes are not recorded.

Lessons begin as candidates and are promoted only after a verified correction, two independent successful supports, or a convention backed by two sources. Retrieval uses normalized lexical similarity plus confidence; it is private and inexpensive, but it is not equivalent to embedding search.

Add the ledger directory to target projects:

```gitignore
.intent-clause/
```

<details>
<summary><strong>Signing key locations and overrides</strong></summary>

The default machine key is stored at `%LOCALAPPDATA%/intent-clause/memory.key` on Windows or `$XDG_CONFIG_HOME/intent-clause/memory.key` / `~/.config/intent-clause/memory.key` elsewhere.

Set `INTENT_CLAUSE_KEY_FILE` only when an organization manages the key location. `INTENT_CLAUSE_SIGNING_KEY` is intended for isolated tests and automation.

</details>

### Optional remote layer

No remote provider adapter ships in this version. The extension contract is documented in [`references/remote-intelligence.md`](references/remote-intelligence.md).

Any future Gemini, DeepSeek, or other adapter must remain disabled by default. An available API key is never treated as consent. The adapter must disclose exactly what leaves the machine, redact and bound payloads, and fall back locally. Providers are not described as free because quotas, pricing, retention, and terms can change.

## Model and Effort Routing

After showing the master prompt, IntentClause classifies execution from `M0` through `M3`:

| Class | Typical scope | Recommended capability | Effort |
|---|---|---|---|
| `M0` | Mechanical formatting or supplied-text transformation | Economy or fast | Minimal or low |
| `M1` | Focused local edit or bounded lookup | Economy or balanced | Low |
| `M2` | Cross-file implementation, debugging, or routine sensitive work | Balanced | Medium |
| `M3` | Architecture, broad ambiguity, or high-risk work | Frontier | High |

Risk floors take precedence: `R2` work requires at least `M2`, and `R3` work requires `M3`. Cost reduction cannot silently weaken sensitive work.

The active model and effort are accepted only from host runtime metadata, configuration confirmed for the active turn, or an explicit user statement. Unknown values remain `UNKNOWN`; IntentClause never searches project files for the host model, guesses from writing style or credentials, or claims to switch models without a real host tool. Task classification still always produces a capability-class and effort recommendation; runtime detection is needed only for the fit comparison. In OpenCode, users change models through `/models` and the provider-supported variant selector.

## Project Structure

```text
intent-clause/
|-- .github/workflows/validate.yml
|-- adapters/                 # Host command adapters
|-- agents/openai.yaml        # Codex skill policy
|-- assets/                   # Master prompt template
|-- evals/                    # Behavioral calibration cases and fixtures
|-- modules.json              # Declarative selective-loading registry
|-- references/               # Progressive-disclosure guidance and domain modules
|-- scripts/
|   |-- context_router.py     # Bounded project evidence planner
|   |-- install.py            # Host-aware installer
|   |-- memory.py             # Signed local lesson ledger
|   `-- validate_skill.py     # Project invariant validator
|-- tests/test_tools.py
|-- SKILL.md                  # Mandatory orchestration flow
`-- README.md
```

`SKILL.md` is a compact orchestration kernel. Detailed references are selected through `modules.json` and loaded only when relevant, following the Agent Skills progressive-disclosure model.

## Validation

Run the dependency-free project checks:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

If [`skills-ref`](https://pypi.org/project/skills-ref/) is installed, validate the Agent Skills specification as well:

```bash
agentskills validate /absolute/path/to/intent-clause
```

Use an absolute path with `skills-ref 0.1.1`; its CLI may treat `.` as an empty directory name during the required folder-name check.

Behavioral calibration specifications live in [`evals/cases.json`](evals/cases.json). They cover manual-only invocation, context tiers, Graphify routing, no-learning fast paths, project discovery, latent intent, prompt-only operation, approvals, prompt injection, failed verification, and frontend ambiguity. The local validator checks their structure; it does not run an agent or claim behavioral conformance. See [`evals/README.md`](evals/README.md) for the manual protocol.

## Design Principles

- Depth means better decisions, not a longer prompt.
- Project evidence beats assumptions.
- Questions are reserved for divergent decisions.
- Security controls must map to plausible risks.
- Optimization requires a metric, baseline or proxy, guardrail, and evidence.
- The shown master prompt and actual execution must not drift apart.
- No test, benchmark, deployment, or review is reported unless it happened.
- Context retrieval stops when prompt-relevant evidence is sufficient.
- Memory promotion requires verification or repeated independent support.
- Remote disclosure is explicit, minimal, and approved per run.

## Roadmap

- Executable behavioral eval runner for multiple agent hosts.
- Additional domain adapters and multilingual calibration cases.
- Optional embedding and reranking provider adapters.
- Automated host compatibility tests for Claude Code, Codex, and OpenCode.

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md), preserve the core pipeline and progressive-disclosure structure, and add or update an eval case whenever behavior changes.

Before opening a pull request, run:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

## License

IntentClause is available under the [MIT License](LICENSE).
