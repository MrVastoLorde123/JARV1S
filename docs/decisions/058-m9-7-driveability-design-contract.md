# Decision 058 — M9.7 Driveability Design Contract

## Status

Accepted — design contract for implementation.

## Objective

Driveability is the ability for JARVIS to preserve an explicit user objective across bounded cycles and determine the next bounded step from validated context, without requiring continuous micromanagement.

## Required identities

Every continuation cycle should preserve:

```text
objective_id
cycle_id
parent_cycle_id (when applicable)
proposal_id (when a next step is proposed)
observation/evidence provenance
```

## Required distinctions

```text
Objective ≠ Authorization
Objective Persistence ≠ Objective Mutation
Observation ≠ User Intent
Next-Step Proposal ≠ Execution
Continuation ≠ Permission
Driveability ≠ Unbounded Autonomy
```

## Bounded continuation

A continuation controller may:

- inspect validated observations
- determine whether an objective is still active
- propose the next bounded work item
- hand that work to existing delegation/agency boundaries
- stop on completion, cancellation, policy block, unresolved uncertainty, or explicit bound exhaustion

It may not execute directly or bypass the existing M7–M9.6 authority and capability boundaries.

## Objective integrity

User-established objective state is authoritative input. Derived work may be decomposed from it, but a worker, observation, recovery event, or model interpretation cannot silently replace or broaden the objective.

Explicit user updates, cancellation, or authority-layer decisions are the only mechanisms that may change the objective's governing scope.

## Termination

Every continuation run must have explicit termination conditions. No hidden infinite loop, recursive self-delegation, or indefinite retry cycle is permitted.

## Implementation boundary

M9.7 begins with a deterministic contract. Model-driven next-step selection is downstream of this boundary; model output is a proposal, not authority.
