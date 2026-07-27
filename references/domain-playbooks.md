# Domain Playbooks

Read only the sections matching the task. Project evidence and user decisions override these defaults.

## Software Engineering and APIs

Collect:

- runtime, framework, versions, entry points, public interfaces, data stores, and nearest tests;
- existing error, validation, logging, and dependency conventions;
- compatibility requirements and migration constraints.

Prompt for:

- behavior and edge cases, not implementation alone;
- validation at trust boundaries;
- authorization separate from authentication;
- stable API/error contracts where consumers exist;
- focused tests for happy path, boundaries, failures, and regressions;
- no unrelated refactors or speculative abstractions.

Verify with the project's formatter, static checks, focused tests, and build where proportionate.

## Frontend and Product Design

Collect:

- product/page type, audience, primary action, existing design system, brand assets, content, target devices, and accessibility constraints;
- current components and styling conventions before inventing new ones.

Prompt for:

- one explicit design read tied to subject and audience;
- coherent typography, color, spacing, shape, imagery, and motion decisions;
- responsive behavior for each nontrivial layout;
- keyboard, focus, contrast, semantic markup, reduced motion, loading, empty, and error states;
- real content/assets where available and no fabricated claims or metrics;
- visual validation at representative desktop and mobile sizes.

Optimization priorities may include LCP/INP/CLS, asset weight, conversion clarity, and maintainable tokens. Do not trade accessibility for visual novelty.

## Data, Analytics, and Machine Learning

Collect:

- decision being supported, data source and ownership, schema, time range, quality issues, leakage risks, target metric, and reproducibility requirements.

Prompt for:

- explicit definitions and units;
- data validation, missingness, outliers, bias, leakage, and train/evaluation separation;
- baseline comparison and uncertainty;
- reproducible seeds, versions, and transformations;
- no fabricated data, citations, performance, or causal claims;
- privacy and retention controls for sensitive records.

Acceptance must distinguish exploratory findings from production claims.

## DevOps, Cloud, and Databases

Collect:

- environments, provider/runtime, state ownership, deployment strategy, traffic/data criticality, access model, observability, backup, and rollback capabilities.

Prompt for:

- declarative and idempotent changes;
- least privilege and secret-manager usage;
- plan/dry-run before apply where supported;
- health checks, staged rollout, migration compatibility, backup, rollback, and partial-failure handling;
- cost and resource boundaries;
- explicit approval before production mutation.

Never infer production authorization from permission to edit configuration.

## Security and Privacy

Collect:

- assets, actors, trust boundaries, data classification, abuse cases, deployment context, compliance constraints, and current controls.

Prompt for:

- scoped threat model;
- findings ranked by exploitability and impact;
- evidence and affected locations;
- remediation preserving legitimate behavior;
- tests demonstrating both exploit prevention and expected use;
- responsible handling of exploit details and secrets.

Do not claim a system is secure because a checklist passed.

## Research, Writing, and Documentation

Collect:

- audience, purpose, decision/use case, scope, date sensitivity, source standard, tone, length, and required format.

Prompt for:

- claims separated from interpretation;
- primary or authoritative sources for consequential/current facts;
- citations that actually support each claim;
- explicit uncertainty and source dates;
- audience-appropriate structure and terminology;
- no invented quotes, statistics, references, or access claims.

Verification includes link/source checks, consistency, factual review, and format linting where available.

## Business, Product, and Marketing

Collect:

- audience/segment, problem, desired behavior, offer, channel, funnel stage, brand constraints, evidence, and legal boundaries.

Prompt for:

- one primary outcome and measurable success signal;
- claims grounded in supplied evidence;
- audience-specific language and objections;
- differentiation based on product truth, not generic superlatives;
- privacy-respecting analytics and no deceptive urgency, fake social proof, or dark patterns;
- experiments with hypotheses and decision thresholds when optimization is requested.

## High-Stakes Domains

This includes legal, medical, financial, employment, physical safety, and regulated workflows.

Collect:

- jurisdiction, affected person, decision authority, evidence date, professional review requirements, and consequence of error.

Prompt for:

- bounded informational assistance;
- explicit uncertainty and missing evidence;
- authoritative, current sources;
- human review before consequential action;
- privacy and auditability;
- safe escalation or emergency guidance when applicable.

Do not execute consequential decisions on behalf of a qualified professional or affected person.
