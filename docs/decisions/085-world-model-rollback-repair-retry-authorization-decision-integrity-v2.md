# Decision 085 — World Model Rollback Repair Retry Authorization Decision Integrity v2

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Context
M23.50 produces immutable authorization decision evidence from one M23.49 proposal. A distinct integrity boundary is required before any execution preparation can consume that decision.

## Decision
M23.51 verifies one exact M23.49 proposal against one exact M23.50 decision. Integrity is evidence validation, not renewed authorization.

The verifier requires matching proposal/decision identity, lineage, environment/model identity, requested action, eligibility, retry bounds, timing, and action/decision consistency. `RETRY_REPAIR + eligible=True` must be `ACCEPT`; `NO_AUTHORIZATION + eligible=False` must be `REJECT`.

## Authority Boundary
- Integrity ≠ Authorization.
- Integrity ≠ Execution.
- ACCEPT ≠ Execution.
- VALID ≠ Permission to bypass downstream preparation.
- Integrity verification does not schedule, execute, persist, or mutate policy.

## Explicitly Deferred
Execution preparation/handoff, execution, result integrity, outcome classification, feedback, persistence/history, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain downstream boundaries.
