# Decision 029 — Consequence Learning-State Application Boundary

## Status

Proposed implementation boundary for M44.

M43 creates an inert application request. M44 introduces the first explicit learning-state mutation boundary by requiring an injected applicator and returning an immutable application receipt.

## Decision

Introduce `ConsequenceLearningStateApplicationService` as the M43 application-request → bounded learning-state application bridge.

```text
M42 Learning-State Consumption
  ↓
M43 Learning-State Application Request
  ↓
M44 Learning-State Application
  ↓
Applied Learning State + Application Receipt
```

## Contract

- Application consumes only an M43 `ConsequenceLearningStateApplicationRequest`.
- Application requires an explicitly injected applicator; no storage or memory backend is selected implicitly.
- The applicator receives the exact request lineage and payload and returns a non-empty application record identity.
- M44 records that mutation occurred only after the applicator successfully returns an application identity.
- Application does not grant authorization, execution authority, retry authority, revocation authority, or semantic truth.
- M44 is not a policy decision and cannot reinterpret the learning payload.

## Authority walls

```text
Application Request ≠ Application Success
Application Success ≠ Authorization
Application Success ≠ Execution
Application Success ≠ Retry Authority
Application Success ≠ Truth Authority
```

## Verification

Focused M44 tests, M43 compatibility, and full agent regression are required before VERIFIED / COMPLETE.
