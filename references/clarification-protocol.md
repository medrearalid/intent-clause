# Clarification Protocol

The goal is to remove decision-divergent ambiguity with minimal interruption.

## Ambiguity Classes

| Class | Definition | Action |
|---|---|---|
| Blocking | Plausible answers change architecture, safety, irreversible action, cost, or core acceptance | Ask before compiling the final prompt |
| Material but inferable | Answers matter, but project evidence supports a safe reversible default | Proceed and label the assumption |
| Cosmetic | Preference changes presentation but not task success | Use existing convention or a sensible default |
| Discoverable | Workspace or authoritative documentation can answer | Inspect; do not ask |

## Decision-Divergence Test

For each unknown:

1. Write two plausible answers internally.
2. Compare their effect on deliverables, implementation, risk, and verification.
3. If the resulting work differs materially, the unknown is decision-divergent.
4. Check whether project evidence resolves it.
5. Ask only if no safe, evidence-backed default remains.

## Question Budget

- Simple `R0`: zero questions by default; at most one.
- Normal `R1`: zero to two questions.
- Sensitive `R2`: ask every unresolved safety-critical decision, grouped into one compact batch where possible.
- High-risk `R3`: no numerical cap, but each question must map to a named risk or approval boundary.

The budget is a discipline, not permission to skip a critical question.

## Good Question Form

Use:

> Which compatibility target should be preserved: **A**, **B**, or **C**? I recommend **A** because [one consequence].

Avoid:

> Please provide your goals, users, stack, design, timeline, budget, security requirements, performance needs, and preferred output format.

## Ask at the Right Time

- Ask before editing when answers change the implementation.
- Ask immediately before an external/destructive action when approval is the only missing item.
- Do not ask hypothetical deployment questions for a local prototype unless deployment is in scope.
- Do not ask the user to choose a technical detail already established by the repository.

## Defaults

A default is acceptable only when it is:

- compatible with verified project conventions;
- reversible without data loss;
- low-risk;
- unlikely to surprise an affected user;
- stated if it materially shapes the result.

Silence is not consent for destructive, costly, public, privileged, or irreversible actions.
