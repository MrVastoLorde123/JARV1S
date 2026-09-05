# Decision 034 — Adaptation Feedback → Evaluation Boundary

## Decision

An `LearningWriteAdaptationFeedbackEvent` becomes a separate immutable evaluation candidate before any adaptation decision, adaptation write, learning-state update, or memory mutation.

## Rationale

Adaptation feedback is an observation derived from an integrity-checked outcome. It must not be treated as truth or authorization. A dedicated evaluation boundary makes interpretation explicit, preserves lineage, and creates a stable point for future policy or decision logic.

## Contract

- Input is an exact `LearningWriteAdaptationFeedbackEvent`.
- Output is an immutable `LearningWriteAdaptationFeedbackEvaluationCandidate`.
- Successful feedback becomes `ADAPTATION_SUCCESS_SIGNAL`.
- Failed feedback becomes `ADAPTATION_FAILURE_SIGNAL`.
- Execution, admission, proposal, decision, adaptation-candidate, source-feedback, source-candidate, and domain identity are preserved.
- Evidence and provenance are recursively frozen.
- Evaluation identifiers are deterministic for identical source evidence.
- Evaluation confidence is explicitly bounded to `[0.0, 1.0]`.
- Evaluation is interpretive evidence only; it does not grant authority, authorization, retry, revocation, execution, learning-write, or memory-mutation authority.

## Authority walls

- Adaptation Feedback ≠ Adaptation Evaluation
- Evaluation ≠ Adaptation Truth
- Evaluation ≠ Authorization
- Evaluation ≠ Retry Authorization
- Evaluation ≠ Revocation
- Evaluation ≠ Execution
- Evaluation ≠ Memory Mutation
- Observation ≠ Certainty
- Learning ≠ Authority
