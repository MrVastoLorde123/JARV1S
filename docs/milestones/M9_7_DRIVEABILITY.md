# M9.7 — Driveability / Objective Continuation

## Status

**Design contract accepted — implementation next.**

M9.7 is the final workforce milestone. It introduces bounded objective continuation: JARVIS can preserve an explicit user objective across work cycles, inspect validated observations, and propose the next bounded action or delegation step without requiring constant micromanagement.

## Roadmap position

```text
M9.1  Worker Identity / Assignment Boundary       ✅
M9.2  Bounded Worker Runtime                      ✅
M9.3  Worker Context / Knowledge Boundary          ✅
M9.4  Worker Reporting / Result Integration        ✅
M9.5  Delegation / Coordination                   ✅
M9.6  Workforce Reliability / Recovery            ✅
M9.7  Driveability / Objective Continuation       → implementation
```

## Core invariant

```text
JARVIS may maintain an objective without granting itself authority.
```

## Authority walls

```text
Objective Continuation ≠ Authorization
Driveability ≠ Permission
Planning ≠ Execution
Next-Step Selection ≠ Authority
Goal Persistence ≠ Goal Mutation
Observation ≠ User Intent
```

## Required behavior

A continuation cycle must preserve objective identity and provenance, operate on validated context, produce only bounded proposals or delegations, and stop on explicit completion, cancellation, blocking, uncertainty, or bound exhaustion.

Every executable action continues through the established M7–M9.6 boundaries.
