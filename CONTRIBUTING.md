# Contributing

IntentClause is an instruction system, so behavioral precision matters more than document length.

## Change Process

1. Describe the failure mode or missing behavior.
2. Add or update a case in `evals/cases.json` that captures it.
3. Make the smallest change to `SKILL.md` or a focused reference file.
4. Run `python scripts/validate_skill.py`.
5. Test the case in at least one supported host and record the observed behavior in the pull request.

## Authoring Rules

- Keep `SKILL.md` focused on routing and mandatory behavior.
- Put domain detail in a one-level `references/` file.
- Do not add generic best-practice lists without a triggering condition.
- State mechanical gates where reliable behavior matters.
- Use examples to calibrate decisions, not as universal templates.
- Do not require tools or model capabilities unavailable across supported hosts unless compatibility metadata is updated.
- Never include credentials, private prompts, proprietary project data, or fabricated benchmarks.

## Eval Case Requirements

Each case must include:

- a stable unique `id`;
- representative user `input`;
- `expected_mode` and `expected_risk`;
- observable `must` behaviors;
- prohibited `must_not` behaviors.

Prefer adversarial and boundary cases over duplicate happy paths.
