# Decision 023 — Consequence Learning Decision Boundary

## Status

Proposed implementation boundary for M38.

M37 produces an inert evaluation signal. M38 deterministically decides whether that signal is eligible for a later learning write or requires review/deferment. M38 does not write learning state, mutate memory, retry execution, authorize tools, or establish truth.

## Decision

Introduce `ConsequenceLearningDecisionService` as the M37 → M38 bridge.

```text
M35 Consequence Execution Outcome
  ↓
M36 Consequence Execution Feedback
  ↓
M37 Consequence Feedback Evaluation
  ↓
M38 Consequence Learning Decision
  ↓
Separate learning-write / adaptation / retry boundaries
```

## Contract

- `SUCCESS_SIGNAL` becomes `LEARNING_ELIGIBLE`.
- `FAILURE_SIGNAL` becomes `REVIEW_REQUIRED`.
- `NOT_EXECUTED_SIGNAL` becomes `NOT_ELIGIBLE`.
- The decision preserves the complete consequence provenance chain.
- Confidence remains bounded evidence from M37; M38 does not upgrade confidence.
- `LEARNING_ELIGIBLE` means only that a later learning-write boundary may consider the evidence.
- `REVIEW_REQUIRED` requires a separate decision before any learning write.
- `NOT_ELIGIBLE` does not erase or reinterpret the observed evidence.
- No learning state is written by M38.
- No memory mutation, retry request, authorization, execution, revocation, policy mutation, or semantic-truth authority is created.

## Authority walls

```text
Evaluation ≠ Learning Decision
Learning Eligibility ≠ Learning Write
Learning Decision ≠ Retry Authority
Learning Decision ≠ Authorization
Learning Decision ≠ Truth
```

## Verification

Focused M38 tests, coding-service integration tests, M37 compatibility, full agents, and core regression are required before VERIFIED / COMPLETE.
