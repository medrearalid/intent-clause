# Worked Examples

These examples calibrate decisions. They are not copy-paste prompt templates.

## Example 1: Fast Path Copy Task

Input:

> Make this email more professional.

Intent read: improve clarity and credibility for the recipient without changing the message.

Behavior:

- `R0`, no project context needed.
- If email body and audience are present, ask no question.
- Compile a compact prompt specifying audience, preserved facts, tone, deliverable, and no invented commitments.
- Show the prompt, rewrite the email, and report that no external fact check was needed.

Failure to avoid: adding a long security checklist or asking ten brand-voice questions.

## Example 2: Codebase Change

Input:

> Make login safer and faster.

Context inspection:

- authentication flow and middleware;
- password/session/token settings;
- database queries and indexes;
- rate limiting and audit logs;
- client compatibility and tests.

Likely profile:

- `R2` due to authentication.
- Safety priorities: enumeration resistance, authorization/session correctness, secret hygiene, bounded abuse controls, safe logs.
- Optimization priority: measured authentication latency without weakening password hashing or controls.

Clarify only if repository evidence cannot resolve a decision such as compatibility or identity-provider ownership.

Acceptance examples:

- Existing clients retain the documented response contract.
- Enumeration behavior is uniform for known and unknown accounts.
- Abuse controls have focused tests.
- Before/after latency is reported under the same workload; no invented percentage.

## Example 3: Frontend Brief

Input:

> Build a premium landing page for my security product.

Intent read: establish trust and convert a defined technical audience, not merely add luxury styling.

Inspect:

- product truth, audience, current framework, brand assets, design system, content, and existing page.

Potential blocking question:

> Is the primary visitor a security engineer evaluating technical depth or an executive evaluating business risk? I recommend choosing one primary audience because it changes the page hierarchy and proof.

Prompt requirements:

- declare a specific visual direction based on security artifacts and audience;
- avoid generic dark-tech neon defaults unless the brief supports them;
- use evidence-backed claims only;
- define responsive, accessible, loading/error, and reduced-motion behavior;
- validate representative mobile and desktop views.

## Example 4: Production Migration

Input:

> Move our production database to the new schema tonight.

Behavior:

- `R3`; inspect migration, data volume, compatibility, backup, replicas, deployment sequence, and rollback.
- Compile the plan and perform safe local/staging validation.
- Require explicit approval immediately before production mutation.
- Never infer production authorization from repository access.
- Stop if backup/rollback or compatibility cannot be established.

Failure to avoid: running the migration because the user asked generally, without naming target, impact, evidence, and rollback at the approval gate.
