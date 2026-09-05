# M22.15 — Feedback Evaluation / Learning Candidate Boundary

## Purpose

Establish the first explicit evaluation layer between inert execution feedback and any learning or memory decision.

## Contract

- `FeedbackEvaluationService` accepts only `ExecutionFeedbackEvent`.
- Evaluation produces an immutable `LearningCandidate`.
- The candidate preserves feedback, execution, and handoff provenance.
- Success, tool failure, and executor failure become distinct learning-signal classifications.
- Confidence is explicit and bounded rather than treated as certainty.
- The candidate requires a later learning decision before memory or learning state can change.

## Boundary

```text
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
Memory / Learning Decision
```

## Authority walls

```text
Feedback ≠ Learning
Feedback Evaluation ≠ Learning Write
Learning Candidate ≠ Memory
Learning Candidate ≠ User Intent
Evidence ≠ Truth
Confidence ≠ Certainty
Outcome ≠ Permission
Learning ≠ Authority
```

## Deliberate exclusions

No durable learning writes, memory mutation, automatic retry, re-authorization, revocation, execution, or alternate memory-decision path is introduced.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.15 becomes VERIFIED / COMPLETE only after the user's local focused and regression receipt passes.
