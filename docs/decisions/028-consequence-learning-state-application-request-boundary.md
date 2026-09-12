# Decision 028 — Consequence Learning-State Application-Request Boundary

## Status

Proposed implementation boundary for M43.

M42 admits independently verified persisted learning state for downstream consumption. M43 introduces an explicit, inert request boundary before any learning-state application or mutation occurs.

## Decision

Introduce `ConsequenceLearningStateApplicationRequestService` as the M42 consumption → application-request bridge.

```text
M39 Learning Write Request
  ↓
M40 Persistence
  ↓
M41 Persistence Verification
  ↓
M42 Learning-State Consumption
  ↓
M43 Learning-State Application Request
  ↓
Later explicit application/mutation boundary
```

## Contract

- Application-request creation requires an immutable M42 consumption result.
- The consumed payload and full verification lineage are preserved exactly.
- M43 creates intent for a later application stage but performs no state mutation itself.
- No storage write, repair, retry, authorization, execution, revocation, or semantic reinterpretation occurs.
- An application request does not grant authority merely because its source learning state was verified and consumed.

## Authority walls

```text
Learning-State Consumption ≠ Application Request
Application Request ≠ State Mutation
Application Request ≠ Authorization
Application Request ≠ Execution
Application Request ≠ Retry Authority
Application Request ≠ Truth Authority
```

## Verification

Focused M43 tests, M42 compatibility, and full agent regression are required before VERIFIED / COMPLETE.
