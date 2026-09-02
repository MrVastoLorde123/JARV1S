# Decision 052 — M8.6 Agency Reliability / Recovery

## Context

M8.5 provides bounded sequencing of independently authorized execution handoffs. M8.6 must make failure, interruption, partial completion, retry eligibility, and reconciliation explicit without becoming a second authority system.

## Decision

Reliability is represented as explicit state and bounded recovery data around existing M8 execution/lifecycle components. It may classify observed conditions and describe a bounded recovery path, but it may not manufacture authorization, execution requests, credentials, provider handles, or hidden retries.

## Constraints

1. Failed execution remains failed evidence.
2. Interruption remains distinguishable from failure.
3. Partial completion cannot be treated as full success.
4. Retry eligibility is data, not authorization.
5. Any retry or follow-up action requires a fresh M7 authority chain and `ExecutionPreparation`.
6. Recovery budgets are finite and explicit.
7. Exhausted recovery bounds terminate deterministically.
8. Reconciliation uses known evidence and does not infer missing success.
9. Original and follow-up execution identities remain distinct and traceable.
10. M8.6 does not replace `ExecutionLifecycle`, `ControlledAgency`, or plan-level `ExecutionState`.

## Consequence

JARVIS gains bounded reliability semantics while preserving the central authority wall: reliability can describe and constrain recovery, but only M7 can authorize a new executable action.
