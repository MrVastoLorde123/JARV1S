# Decision 033 — Adaptation Outcome → Feedback Boundary

## Decision

An `LearningWriteAdaptationOutcome` becomes a separate immutable feedback event before any future adaptation evaluation, learning-state update, or memory mutation.

## Rationale

Adaptation execution produces an observation about one attempted change. That observation must remain distinct from downstream interpretation. Feedback provides a stable evidence boundary that preserves lineage and makes later evaluation explicit rather than silently treating an outcome as truth.

## Contract

- Input is an exact `LearningWriteAdaptationOutcome`.
- Output is an immutable `LearningWriteAdaptationFeedbackEvent`.
- Successful outcomes become `ADAPTATION_SUCCESS` feedback.
- Failed outcomes become `ADAPTATION_FAILURE` feedback.
- Execution, admission, proposal, decision, adaptation-candidate, source-learning-feedback, source-learning-candidate, and domain identity are preserved.
- Successful payload includes the adaptation result and its existing result fingerprint.
- Failed payload includes the failure reason.
- Feedback identifiers are deterministic for identical source evidence.
- Payload and provenance are recursively frozen snapshots.
- Feedback is evidence only; it is not truth, authorization, retry authorization, revocation, execution, or memory mutation.

## Authority walls

- Adaptation Outcome ≠ Adaptation Feedback
- Feedback ≠ Adaptation Truth
- Feedback ≠ Learning Truth
- Feedback ≠ Authorization
- Feedback ≠ Retry Authorization
- Feedback ≠ Revocation
- Feedback ≠ Memory Mutation
- Observation ≠ Certainty
- Learning ≠ Authority
