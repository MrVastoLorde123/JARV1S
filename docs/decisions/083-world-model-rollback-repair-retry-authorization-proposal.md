# Decision 083 — World Model Rollback Repair Retry Authorization Proposal

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Context
M23.48 produces a bounded, observational retry re-eligibility assessment. That assessment may report `ELIGIBLE`, `WAITING`, or `NOT_ELIGIBLE`, but it does not grant retry permission. JARVIS must preserve the separation between assessment, proposal, authorization, and execution.

## Decision
M23.49 introduces `EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService` as the explicit proposal boundary.

The service consumes exactly one immutable M23.48 re-eligibility assessment and produces one immutable advisory proposal.

`ELIGIBLE` produces `RETRY_REPAIR`, which requests a separate authorization decision.

`WAITING` and `NOT_ELIGIBLE` produce `NO_AUTHORIZATION`; waiting evidence is never converted into a retry request before its eligibility boundary is satisfied.

The proposal preserves assessment, evaluation, feedback, outcome, environment, model, retry-count, retry-bound, timing, reasons, and lineage evidence.

## Authority Boundary

- Proposal ≠ Authorization.
- Proposal ≠ Execution.
- Assessment ≠ Permission.
- ELIGIBLE ≠ Authorized.
- WAITING ≠ Retry Permission.
- NOT_ELIGIBLE ≠ Automatic Retry.
- Proposal generation does not schedule retry.
- Proposal generation does not mutate policy or persistence.
- Proposal generation does not assign work or select an executor.

## Integrity and Immutability

The proposal is a frozen dataclass. Reasons and lineage are recursively frozen. The source assessment is never mutated.

The next boundary is a distinct authorization decision artifact and must consume the exact proposal identity and evidence rather than infer authorization from status alone.

## Explicitly Deferred

Authorization decision, authorization integrity, execution preparation, execution, outcome classification, feedback, persistence/history, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.
