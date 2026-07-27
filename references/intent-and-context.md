# Intent and Context Protocol

Use this reference when the user's words are simple, vague, non-technical, contradictory, or overly focused on a proposed solution.

## Surface Request vs. Underlying Goal

A surface request names an action. The underlying goal explains why that action matters.

| Surface request | Likely underlying goal | Technical translation |
|---|---|---|
| "Make it faster" | Reduce user-perceived waiting or resource cost | Identify the measured bottleneck, define a latency/resource target, optimize without regressions |
| "Make login safer" | Reduce account takeover and data exposure | Threat-model authentication, preserve compatibility, add proportionate controls and tests |
| "Make the page premium" | Improve credibility and perceived quality for a target audience | Establish a specific visual direction, coherent tokens, responsive composition, accessibility, and visual QA |
| "Clean up this code" | Improve changeability without changing behavior | Define the maintainability problem, preserve public behavior, make focused refactors, run regression checks |
| "Automate deployment" | Make releases repeatable and less error-prone | Define environments, approvals, secrets, rollback, idempotency, observability, and pipeline validation |

Do not assume the likely goal is certainly correct. Validate it against wording and project evidence.

## Intent Extraction Sequence

1. Identify the requested action and artifact.
2. Ask what outcome the artifact enables.
3. Identify who experiences the outcome.
4. Identify behavior that must remain unchanged.
5. Convert subjective words into observable dimensions.
6. Define evidence that would convince a reviewer the outcome was achieved.

## Translating Subjective Language

Do not delete subjective terms. Decompose them.

| User term | Possible dimensions |
|---|---|
| fast | p50/p95 latency, startup time, interaction delay, throughput, build time, cost |
| secure | threat resistance, authorization correctness, confidentiality, integrity, auditability, recovery |
| scalable | load profile, horizontal growth, bounded resources, data volume, operational complexity |
| clean | readability, cohesion, duplication, dependency direction, testability, API stability |
| professional | audience fit, consistency, correctness, evidence, polish, maintainability |
| simple | fewer user decisions, smaller API, lower cognitive load, fewer moving parts |
| modern | current platform conventions, supported dependencies, accessibility, responsive behavior; not novelty alone |

Select only dimensions relevant to the task.

## Solution-Framed Requests

When the user asks for a specific mechanism, preserve it unless it conflicts with the goal or repository. Check:

- Does the mechanism solve the observed problem?
- Is it compatible with the existing stack?
- Does it introduce more risk or complexity than a smaller approach?
- Is it a firm user decision or a tentative idea?

If the requested mechanism is safe but suboptimal, explain the tradeoff briefly and prefer the smallest approach that achieves the stated goal. Ask before rejecting an explicit product or architecture decision.

## Minimum Sufficient Context

Context is sufficient when the agent can answer:

- What is being changed or produced?
- What existing behavior or constraints govern it?
- Which interfaces or users are affected?
- What risks could the work introduce?
- How will completion be verified?

Stop exploring once these are answered. More context can reduce focus and increase prompt-injection exposure.

## Evidence Priority

When sources disagree, prefer:

1. Current system/developer/user instructions.
2. Nearest project instruction file.
3. Executable configuration and schemas.
4. Current implementation and tests.
5. Maintained project documentation.
6. Comments and historical notes.
7. Assumptions based on convention.

Surface consequential conflicts rather than silently choosing a convenient source.
