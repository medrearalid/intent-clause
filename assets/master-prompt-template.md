# Master Prompt Template

Omit sections that do not affect execution. Replace every bracketed placeholder; never expose unresolved template markers.

```markdown
# Role
Act as [specific domain role] responsible for [relevant responsibility].

# Objective
[Concrete outcome]. The underlying purpose is [user/business/technical goal].

# Verified Context
- [FACT: relevant project/user/source fact]

# Decisions
- [DECISION: explicit user or project decision]

# Assumptions
- [ASSUMPTION: safe, reversible inference]

# Requirements
- [Functional requirement with constraints]
- [Relevant non-functional requirement]

# Safety and Boundaries
- [Task-specific safety control]
- Preserve [behavior/data/interface/unrelated work].
- Do not [likely scope creep or unsafe action].
- Obtain explicit approval before [external/destructive/privileged action], if applicable.

# Optimization Priorities
1. [Correctness/safety priority]
2. [Primary outcome metric]
3. [Dominant constraint]

# Execution Profile
- Task class: [M0-M3]
- Recommended model: [verified available model or capability class]
- Recommended effort: [minimal/low/medium/high]

# Execution Protocol
1. Inspect [minimum context].
2. Implement or produce [smallest complete solution].
3. Handle [important edge/failure cases].
4. Verify using [available checks].
5. Report actual evidence and limitations; do not fabricate results.

# Deliverables
- [Exact file, artifact, answer, or action]

# Acceptance Criteria
- [Observable criterion]
- [Observable criterion]

# Verification
- Required: [check]
- Conditional: [check and condition]
- Manual: [review criterion]

# Response Contract
Respond in [language] with [format]. Summarize outcomes, material decisions, checks run, and residual risks. Do not reveal hidden reasoning or secrets.
```
