# Decision 025 — Consequence Learning-State Persistence Boundary

## Status

Proposed implementation boundary for M40.

M39 creates an immutable request to write learning state. M40 is the first boundary permitted to cross from a write request into a persistence authority. The persistence authority is injected; M40 does not invent storage policy, retry policy, or semantic truth.

## Decision

Introduce `ConsequenceLearningStatePersistenceService` as the M39 → persistence bridge.

```text
M38 Learning Decision
  ↓
M39 Learning Write Request
  ↓
M40 Learning-State Persistence
  ↓
Persisted Learning State + Receipt
```

## Contract

- Only a `ConsequenceLearningWriteRequest` may be persisted.
- Persistence requires an explicitly bound writer; no implicit storage is selected.
- The exact M39 payload and full provenance are passed to the writer without reinterpretation.
- A successful write returns an immutable persistence receipt containing the request identity and writer result identifier.
- A failed writer call does not fabricate a successful receipt.
- The service must not authorize, execute, retry, revoke, mutate policy, or establish semantic truth.
- Persistence is a state mutation, but that mutation is limited to the explicitly injected learning-state writer.
- Idempotency is delegated to the writer using the stable M39 request ID.

## Authority walls

```text
Learning Eligibility ≠ Learning Write Request
Learning Write Request ≠ Persistence Success
Persistence Success ≠ Truth Authority
Persistence ≠ Authorization
Persistence ≠ Execution
Persistence ≠ Retry Authority
```

## Verification

Focused M40 persistence tests, M39 compatibility, full agents, and full core regression are required before VERIFIED / COMPLETE.
