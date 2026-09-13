# Decision 036 — Consequence Learning-State Application-Learning Write Request Boundary

## Status

Proposed implementation boundary for M51.

M50 converts confirmed application feedback into an explicit learning-eligibility decision. M51 converts only that eligible decision into an inert application-learning write request. No application-learning state is written or persisted in M51.

## Decision

Introduce `ConsequenceLearningStateApplicationLearningWriteRequestService` as the M50 decision → application-learning write-request bridge.

```text
M48 Application Feedback
  ↓
M49 Application Feedback Evaluation
  ↓
M50 Application Feedback Learning Decision
  ↓
M51 Application-Learning Write Request
  ↓
Later Application-Learning State Persistence
```

## Contract

- The request consumes only an immutable M50 application-feedback learning decision.
- Only `LEARNING_ELIGIBLE` decisions may produce a write request.
- The request preserves the complete application-feedback lineage.
- The request preserves the M50 signal, confidence, and eligibility classification.
- The request carries an immutable application-learning payload derived from the decision metadata without mutating the original learning payload.
- Request creation does not write, persist, verify, repair, retry, authorize, execute, revoke, or mutate memory.
- The request is advisory input for a later persistence boundary.

## Authority walls

```text
Application Learning Decision ≠ Application-Learning Write Request
Application-Learning Write Request ≠ Persistence
Application-Learning Write Request ≠ Memory Mutation
Application-Learning Write Request ≠ Authorization
Application-Learning Write Request ≠ Execution
```

## Verification

Focused M51 tests, M50 compatibility, and full agent regression are required before VERIFIED / COMPLETE.
