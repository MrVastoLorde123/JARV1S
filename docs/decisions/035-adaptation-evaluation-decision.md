# Decision 035 — Adaptation Evaluation → Decision Boundary

## Decision

An `LearningWriteAdaptationFeedbackEvaluationCandidate` becomes a separate immutable decision before any future adaptation proposal, admission, execution, or memory mutation.

## Rationale

Evaluation is evidence about adaptation feedback, not permission to act. A distinct decision boundary prevents evaluation output from silently becoming adaptation authority and preserves a deterministic, inspectable control point before any downstream proposal or execution.

## Contract

- Input is an exact `LearningWriteAdaptationFeedbackEvaluationCandidate`.
- Output is an immutable `LearningWriteAdaptationEvaluationDecision`.
- Evaluation confidence remains bounded to `[0.0, 1.0]`.
- Success evaluation with confidence >= 0.5 becomes `ACCEPT` under the deterministic baseline provider.
- Failure evaluation or confidence < 0.5 becomes `DEFER` under the deterministic baseline provider.
- Exact evaluation, feedback, source-feedback, candidate, source-candidate, execution, admission, proposal, decision, and domain identity is preserved.
- Decision identifiers are deterministic for identical evaluation evidence.
- Provider output identity is validated before returning the decision.

## Authority walls

- Adaptation Evaluation ≠ Adaptation Decision
- Adaptation Decision ≠ Adaptation Authorization
- Decision ≠ Execution
- Decision ≠ Retry Authorization
- Decision ≠ Revocation
- Decision ≠ Memory Mutation
- Evidence ≠ Truth
- Confidence ≠ Certainty
- Learning ≠ Authority
