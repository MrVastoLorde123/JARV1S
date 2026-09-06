# Decision 084 — World Model Rollback Repair Retry Authorization Decision v2

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Context
M23.49 converts M23.48 re-eligibility assessment into an explicit advisory authorization proposal. A separate decision boundary is required so proposal generation cannot become authorization by implication.

## Decision
M23.50 introduces `EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service`.

The service consumes exactly one M23.49 proposal and produces one immutable decision-evidence artifact.

- `RETRY_REPAIR` is accepted only when proposal `eligible` is explicitly true.
- `NO_AUTHORIZATION` is rejected.
- `DEFER` remains representable as a decision artifact but is never fabricated by the service.
- Proposal, assessment, evaluation, feedback, outcome, environment, model, retry-count/bound, and timing lineage are preserved.
- Reasons and lineage are recursively immutable.
- The source proposal is never mutated.

## Authority Boundary

```text
Decision Evidence ≠ Execution
Decision Evidence ≠ Scheduling
Decision Evidence ≠ Persistence Mutation
Proposal ≠ Authorization by implication
Eligible ≠ Executed
ACCEPT ≠ Execution
DEFER ≠ Permission
```

M23.50 remains non-executing. It does not schedule retry, invoke an executor, mutate policy, or mutate persistence/history.

## Compatibility

The M23.49 proposal retains the established M23.39/M23.40 constructor compatibility surface. M23.50 consumes that proposal directly and preserves its legacy metadata when present while also carrying the richer M23.48 lineage fields.

## Explicitly Deferred

Authorization integrity, execution preparation/handoff, execution, result integrity, outcome classification, feedback, re-eligibility, persistence/history, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain downstream boundaries.
