# Decision 027 — Learning Write Feedback → Adaptation Evaluation Boundary

## Context

M22.21 converts a verified `LearningWriteOutcome` into immutable, inert `LearningWriteFeedbackEvent` evidence. The feedback must now be interpretable for adaptation without becoming memory mutation, authorization, retry authority, or execution.

## Decision

Introduce `LearningWriteFeedbackEvaluationService` and `LearningWriteAdaptationCandidate` as the non-mutating evaluation boundary after learning-write feedback.

The boundary:

- consumes only `LearningWriteFeedbackEvent`;
- maps `WRITE_SUCCESS` and `WRITE_FAILURE` to explicit adaptation signals;
- preserves exact feedback, execution, admission, proposal, decision, source-candidate, and domain identity;
- carries recursively frozen evidence and provenance snapshots;
- produces deterministic adaptation-candidate identity;
- uses bounded default confidence without treating success as truth;
- cannot mutate memory or learning state;
- cannot authorize, retry, revoke, or execute tools.

## Boundary

```text
LearningWriteOutcome
↓
LearningWriteFeedback
↓
LearningWriteFeedbackEvaluationService
↓
LearningWriteAdaptationCandidate
↓
Learning / Adaptation Decision
```

## Authority walls

- Learning Write Feedback ≠ Adaptation Candidate
- Adaptation Candidate ≠ Learning Truth
- Evaluation ≠ Authorization
- Evaluation ≠ Retry Authorization
- Evaluation ≠ Revocation
- Evaluation ≠ Memory Mutation
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## Explicit exclusions

This milestone does not decide whether an adaptation should be accepted, mutate memory or learning state, authorize execution, trigger retries, revoke capabilities, or define persistent stores.
