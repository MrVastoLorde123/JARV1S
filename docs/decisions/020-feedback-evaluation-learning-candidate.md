# Decision 020 — Feedback Evaluation / Learning Candidate Boundary

## Status
Accepted for M22.15.

## Decision
Execution feedback is treated as evidence that must be evaluated before it can influence learning or memory. `FeedbackEvaluationService` converts one immutable `ExecutionFeedbackEvent` into one immutable `LearningCandidate`.

The candidate preserves feedback, execution, and handoff provenance; classifies the observed signal; exposes explicit confidence; and requires a later learning decision.

## Boundary

```text
ExecutionOutcome
↓
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
Memory / Learning Decision
```

## Authority walls

- Feedback ≠ Learning
- Feedback Evaluation ≠ Learning Write
- Learning Candidate ≠ Memory
- Learning Candidate ≠ User Intent
- Evidence ≠ Truth
- Confidence ≠ Certainty
- Outcome ≠ Permission
- Learning ≠ Authority

## Consequences

M22.15 does not persist memory or learning state. It does not call the database, execute tools, authorize requests, retry execution, revoke capabilities, or bypass the existing memory-decision layer.

A later milestone may decide when a learning candidate is strong enough to propose memory creation, confirmation, update, contradiction handling, or explicit rejection.
