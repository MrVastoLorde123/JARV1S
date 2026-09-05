# M22.30 — Adaptation Evaluation → Decision Boundary

## Purpose

Establish a separate decision boundary after adaptation-feedback evaluation so evaluation remains evidence and cannot silently become adaptation authority.

## Contract

- `LearningWriteAdaptationEvaluationDecisionService` consumes an exact `LearningWriteAdaptationFeedbackEvaluationCandidate`.
- `LearningWriteAdaptationEvaluationDecision` is immutable.
- Success evaluation with confidence >= 0.5 is accepted by the deterministic baseline provider.
- Failure evaluation or confidence < 0.5 is deferred.
- Exact evaluation, feedback, source-feedback, adaptation-candidate, source-candidate, execution, admission, proposal, and domain lineage is preserved.
- Decision IDs are deterministic.
- Provider output identity is validated.
- The decision cannot grant adaptation authority, memory mutation, execution authorization, retry, or revocation.

## Boundary

```text
Adaptation Feedback
↓
Adaptation Feedback Evaluation
↓
Adaptation Evaluation Decision
↓
Future Adaptation Proposal / Admission
```

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

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_decision -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.29 is locally verified:

- 11/11 focused
- 502/502 core regression
- 513/513 total
