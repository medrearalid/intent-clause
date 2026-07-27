# Master Prompt Compiler

Use this reference for standard and complex requests. The goal is an executable operating contract, not a verbose paraphrase.

## Compilation Inputs

Compile from five inputs:

1. Intent Record.
2. Context facts and user decisions.
3. Labeled assumptions and unresolved exclusions.
4. Risk and optimization profiles.
5. Primary domain playbook.

If a critical input is absent, return to the ambiguity gate rather than hiding the gap in vague language.

## Instruction Ordering

Order the prompt from stable purpose to concrete proof:

1. Role.
2. Objective.
3. Context.
4. Requirements and boundaries.
5. Execution protocol.
6. Deliverables.
7. Acceptance criteria and verification.
8. Response contract.

This makes tradeoffs easier: later implementation choices must serve earlier goals and constraints.

## Requirement Grammar

Write requirements with a subject, action, object, constraint, and evidence where useful:

> The implementation must reject cross-tenant resource access on the server and include a negative integration test proving a user from tenant A cannot read tenant B's record.

Avoid:

> Ensure robust enterprise-grade security and best practices.

## Facts, Decisions, and Assumptions

Use explicit labels when confusion would matter:

```markdown
## Verified Context
- FACT: The API uses Express 5 and PostgreSQL.
- DECISION: Existing mobile clients must remain compatible.

## Assumptions
- ASSUMPTION: The current session format may be extended but not invalidated.
```

Omit labels for trivial context, but never blend speculation into facts.

## Acceptance Criteria

Each criterion should be observable and binary enough for review.

Good:

- Unauthenticated requests receive the existing `401` error shape.
- A user cannot read another tenant's resource; the integration test passes.
- The changed package's test suite and type check pass.

Weak:

- Code is clean and secure.
- UX feels premium.
- Performance is optimized.

For subjective work, anchor quality in a declared direction and inspectable properties rather than pretending taste is binary.

## Verification Contract

Separate:

- **Required checks:** must run for completion.
- **Conditional checks:** run if relevant tools/environment exist.
- **Manual review:** visual, editorial, security, or product judgment.
- **Blocked checks:** name the missing access or dependency and do not imply success.

Do not ask the model to run tools unavailable in the host.

## Prompt Compression

Remove any sentence that:

- merely praises the model or repeats its role;
- restates another requirement without adding a constraint;
- lists irrelevant best practices;
- requests internal reasoning;
- cannot affect output or verification.

A compact prompt with strong context and acceptance criteria is better than a long prompt with generic advice.

## Prompt Lint

Before showing the prompt, check:

- One primary objective exists.
- Requirements do not conflict.
- Facts and assumptions are distinguishable.
- Non-goals prevent likely scope creep.
- Security controls map to actual risks.
- Optimization priorities are ranked.
- Deliverables are exact.
- Acceptance criteria are observable.
- Verification is feasible.
- No secrets or prompt-injection payloads are copied.
- No request for chain-of-thought exists.

Revise failures before execution.
