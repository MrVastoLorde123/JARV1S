# M22.23 — Learning Write Adaptation Decision Boundary

## Purpose

Establish the explicit decision boundary after learning-write feedback evaluation so an adaptation candidate can be accepted, deferred, or rejected without becoming authority or memory mutation.

## Contract

- `LearningWriteAdaptationDecisionService` consumes a `LearningWriteAdaptationCandidate`.
- `LearningWriteAdaptationDecision` is immutable and non-authorizing.
- Actions are explicitly `ACCEPT`, `DEFER`, or `REJECT`.
- Exact feedback, execution, admission, proposal, decision, source-candidate, and domain lineage is preserved.
- Baseline decisions are deterministic.
- Metadata is recursively frozen.
- Confidence is bounded to [0.0, 1.0].
- Write/mutation/authority flags cannot be enabled.

## Boundary

```text
LearningWriteFeedback
↓
LearningWriteFeedbackEvaluation
↓
LearningWriteAdaptationCandidate
↓
LearningWriteAdaptationDecision
↓
Future Adaptation Proposal
```

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_decision -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.22 is locally verified:

- 11/11 focused
- 502/502 core regression
- 513/513 total
