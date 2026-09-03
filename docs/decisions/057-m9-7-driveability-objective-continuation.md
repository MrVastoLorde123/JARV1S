# Decision 057 — M9.7 Driveability / Objective Continuation

## Status

Accepted — M9.7 implementation in progress.

## Decision

M9.7 introduces bounded objective continuation: JARVIS may maintain an explicit user objective across time, inspect current state, identify the next bounded action or delegation step, and continue from validated observations without requiring the user to restate the objective after every completed step.

Driveability is **not** autonomous authority. Objective continuation may determine what should be considered next, but it cannot authorize execution, broaden capabilities, acquire credentials, bypass policy, or silently redefine the user's objective.

## Core invariants

```text
Objective Continuation ≠ Authorization
Driveability ≠ Permission
Planning ≠ Execution
Next-Step Selection ≠ Authority
Goal Persistence ≠ Goal Mutation
Context Observation ≠ User Intent
```

## Continuation boundary

A continuation cycle must carry a stable objective identity and explicit provenance from the observations that caused the next-step proposal. A next step must be bounded by existing worker, delegation, capability, policy, and M7/M8 authority constraints.

## Objective integrity

The system must distinguish:

- the objective originally established by the user
- derived sub-objectives and bounded work items
- observations produced while pursuing the objective
- proposed next actions
- explicit objective updates or cancellation

JARVIS may decompose an objective, but may not silently replace, broaden, or reinterpret the objective as authorization.

## No hidden agency

M9.7 must not:

- create authorization
- execute actions directly
- bypass M7/M8
- expand worker capability
- acquire credentials
- treat observations as permission
- silently mutate user objectives
- create unbounded continuation loops
- continue indefinitely without bounded progress/termination conditions

## Relationship to M9.1–M9.6

M9.1–M9.6 establish worker identity, bounded runtime, scoped context, reporting, delegation, and recovery. M9.7 sits above those layers and coordinates their bounded capabilities around a persistent objective while preserving the existing authority chain.
