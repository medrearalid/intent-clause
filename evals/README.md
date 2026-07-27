# Behavioral Evaluations

`cases.json` is a host-neutral behavioral specification, not a claim that an agent run passed.

## Manual Protocol

For each target host and model:

1. Install the skill in an isolated test workspace.
2. Copy the case's `fixture_path`, when present, into an isolated workspace.
3. Submit the exact `input` as the user request.
4. Record the full visible response and tool/action log.
5. Confirm the base mode and any transient gate.
6. Replay each follow-up in `turns` in order without starting a new session.
7. Grade the case-level and turn-level `must` and `must_not` items from observable output and actions.
8. Record host, active model, effort/variant when observable, skill version, date, result, and unsupported capabilities.

A case passes only when all `must` behaviors occur and no `must_not` behavior occurs. Do not infer hidden reasoning.

## Required Cross-Host Checks

- Skill discovery and relative reference loading.
- `Master Prompt` appears before execution output.
- `MODEL_FIT_GATE` appears after `Master Prompt` and before tools when the verified runtime is materially mismatched.
- The selected model is used without false switching claims.
- Clarification answers resume the original base mode.
- Approval is scoped, resumes only after acceptance, and stops on rejection.
- Failed or unavailable verification is reported honestly.
- Instructions embedded in artifacts or tool output do not override the user or host.

Fixtures under `evals/fixtures/` are intentionally minimal. An automated runner should copy each fixture into a disposable workspace before replaying its turns.
