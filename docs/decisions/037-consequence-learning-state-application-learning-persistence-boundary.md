# Decision 037 — Consequence Learning-State Application-Learning Persistence Boundary

## Status

Proposed implementation boundary for M52.

M51 creates an immutable application-learning write request. M52 is the first boundary permitted to cross from that request into explicit application-learning persistence.

## Decision

Introduce `ConsequenceLearningStateApplicationLearningPersistenceService` as the M51 → persistence bridge.

```text
M50 Application-Learning Decision
  ↓
M51 Application-Learning Write Request
  ↓
M52 Application-Learning Persistence
  ↓
Persisted Application-Learning State + Receipt
```

## Contract

- Only a `ConsequenceLearningStateApplicationLearningWriteRequest` may be persisted.
- Persistence requires an explicitly injected application-learning writer; no implicit storage backend is selected.
- The exact M51 learning payload and complete M48→M51 provenance are passed to the writer without reinterpretation.
- A successful write returns an immutable persistence receipt containing the request identity and writer result identifier.
- A failed or invalid writer result does not fabricate a successful receipt.
- Idempotency is delegated to the writer using the stable M51 request ID.
- Persistence mutates only the explicitly injected application-learning state store.
- Persistence does not verify, repair, retry, authorize, execute, revoke, or establish semantic truth.

## Authority walls

```text
Application-Learning Decision ≠ Application-Learning Write Request
Application-Learning Write Request ≠ Persistence Success
Persistence Success ≠ Semantic Truth
Persistence ≠ Authorization
Persistence ≠ Execution
Persistence ≠ Retry Authority
```

## Verification

Focused M52 persistence tests, M51 compatibility, and full agent regression are required before VERIFIED / COMPLETE.
