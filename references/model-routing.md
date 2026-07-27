# Model and Effort Routing

Use this reference after the master prompt is compiled and before execution. The goal is to avoid spending frontier-model reasoning on work that a cheaper model can execute reliably without lowering the task's quality or safety floor.

## Detect the Active Runtime

Record the current model and effort/variant only from, in priority order:

1. model and variant metadata supplied by the host for the active turn;
2. active command or agent configuration when the host confirms it governs this turn;
3. an explicit statement from the user.

Configuration defaults and last-used settings are not proof of the active runtime because command-line flags, agents, commands, or session selection may override them. Never infer a model from writing style, latency, pricing, environment secrets, or provider credentials. Label unavailable fields `UNKNOWN`.

Do not claim to change models or effort. Model changes remain a host/user action unless a real host tool explicitly supports the change. In OpenCode, direct the user to `/models` and the variant selector; model IDs and available variants are provider-specific.

## Task Classes

Choose the lowest class that satisfies the task, then apply the risk floor.

| Class | Typical task | Recommended capability | Effort |
|---|---|---|---|
| `M0` | Supplied-text formatting, extraction, short rewrite, no tools | Economy/fast | Minimal or low |
| `M1` | Focused local edit, one component, bounded lookup, routine `R0-R1` | Economy or balanced | Low |
| `M2` | Cross-file implementation, debugging, normal tool use, `R1-R2` | Balanced | Medium |
| `M3` | Architecture, broad ambiguity, difficult reasoning, `R3` | Frontier | High |

Risk floors override apparent task size:

- `R2` requires at least `M2` and medium effort.
- `R3` requires `M3` and high effort.
- A long input alone does not require a stronger model when the operation is mechanical and bounded.
- A short request can require a stronger model when its hidden execution scope or consequences are broad.

Use exact model names only when the host exposes available models or the user names them. Otherwise recommend a capability class, not an invented model. Provider families change; examples such as a frontier Fable/Opus-class model, balanced Sonnet-class model, or economy Haiku-class model are illustrative rather than availability claims.

## Fit Decision

Compare the verified current runtime with the recommended class:

- **MATCH:** Continue without interruption.
- **OVERPOWERED:** Enter `MODEL_FIT_GATE` when a clearly more expensive capability class or effort level is active than the task requires.
- **UNDERPOWERED:** Enter `MODEL_FIT_GATE` when continuing threatens correctness or the risk floor.
- **UNKNOWN:** Do not fabricate a comparison. Ask one concise question only when the missing model information can materially change cost, safety, or execution quality; otherwise show the class recommendation and continue.

Do not interrupt for negligible differences between adjacent models, unavailable alternatives, `PROMPT_ONLY`, or `PLAN_ONLY`. The gate controls execution, not prompt compilation, so the current model still produces the master prompt before the pause.

## Gate Message

Keep the message compact:

```text
Model Fit
Current: [verified model] / [verified effort or UNKNOWN]
Task: [M0-M3 and short reason]
Recommended: [available exact model or capability class] / [effort]
Reason: [cost, quality, or risk consequence]

Change the model/effort and say "continue", or say "continue with current model" to override once.
```

After the user changes settings, re-read host metadata when available and resume the retained mode. An explicit request to continue with the current model is a one-run override; do not repeat the same gate unless task scope or risk changes materially. Never execute tools while the gate is waiting.
