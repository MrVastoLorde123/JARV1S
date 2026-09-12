# Decision 027 — Consequence Learning-State Consumption Boundary

## Status

Proposed implementation boundary for M42.

M41 independently verifies that persisted learning state matches the original M39 request and M40 persistence receipt. M42 introduces an explicit consumption boundary so verified persisted learning state can be admitted into downstream learning-state use without granting authority or semantic truth.

## Decision

Introduce `ConsequenceLearningStateConsumptionService` as the M41 verification → consumption bridge.

```text
M39 Learning Write Request
  ↓
M40 Persistence
  ↓
M41 Persistence Verification
  ↓
M42 Learning-State Consumption
  ↓
Consumed Learning State
```

## Contract

- Consumption requires the original M39 request paired with its M41 verification result.
- Verification must be successful before consumption is allowed.
- Request and persisted-record identities must match the verification result.
- The consumed learning payload is the immutable payload already carried by the M39 request; M42 does not reinterpret or mutate it.
- Consumption does not write, repair, retry, authorize, execute, revoke, or establish semantic truth.
- Consumption is an explicit admission/read boundary, not an authority boundary.

## Authority walls

```text
Persistence Verification ≠ Learning-State Consumption
Learning-State Consumption ≠ Truth Authority
Learning-State Consumption ≠ Authorization
Learning-State Consumption ≠ Execution
Learning-State Consumption ≠ Retry Authority
Learning-State Consumption ≠ Memory Mutation
```

## Verification

Focused M42 tests, M41 compatibility, and full agent regression are required before VERIFIED / COMPLETE.
