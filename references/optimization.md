# Optimization Protocol

Optimization must be tied to an observed or explicitly prioritized outcome.

## Measurement-First Rule

Before optimizing, define:

- metric: what changes;
- baseline: current value or a method to obtain it;
- target: desired threshold or direction;
- workload: conditions under which it matters;
- guardrails: behavior that must not regress;
- evidence: benchmark, test, audit, or user signal.

If no baseline can be measured, state that limitation and use a defensible proxy. Never invent improvement percentages.

## Priority Model

Rank optimization goals in this order unless the user decides otherwise:

1. Correctness, safety, and data integrity.
2. User-visible outcome.
3. Dominant operational constraint.
4. Maintainability and future change cost.

Do not optimize mutually competing dimensions as if all can be maximized.

## Domain Signals

| Goal | Useful measures | Common guardrails |
|---|---|---|
| Runtime performance | p50/p95/p99 latency, throughput, CPU, memory, I/O | correctness, tail behavior, resource caps |
| Frontend performance | LCP, INP, CLS, JS weight, image bytes | accessibility, visual fidelity, device coverage |
| Cost | requests, tokens, compute time, storage, egress | quality floor, latency, reliability |
| Reliability | error rate, recovery time, retry volume, SLO attainment | idempotency, bounded retries, observability |
| Developer workflow | build/test time, setup steps, failure clarity | reproducibility, compatibility, debuggability |
| UX/conversion | completion rate, task time, error rate, drop-off | accessibility, trust, dark-pattern avoidance |
| Prompt quality | task success, correction turns, unsupported claims, tool errors | intent fidelity, safety, token budget |

## Optimization Sequence

1. Measure or establish a reproducible baseline.
2. Locate the dominant bottleneck or failure source.
3. Choose the smallest intervention likely to affect it.
4. Preserve a control or before/after comparison.
5. Verify the target metric and regression guardrails.
6. Report actual evidence and uncertainty.

## Anti-Patterns

- Adding caches without invalidation, bounds, or a measured need.
- Adding concurrency without ordering, resource, and failure semantics.
- Replacing clear code with complex code for theoretical speed.
- Claiming "production-ready," "SEO-optimized," or "scalable" without criteria.
- Using synthetic benchmarks that do not resemble the relevant workload.
- Expanding dependencies to solve a problem the existing stack already handles.
