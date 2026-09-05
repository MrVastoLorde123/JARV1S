# M22.16 — Learning Decision Boundary

## Purpose

Establish the decision boundary between an inert `LearningCandidate` and any later learning or memory write.

## Contract

- `LearningDecisionService` consumes a `LearningDecisionContext`.
- A replaceable `LearningDecisionProvider` returns an immutable `LearningDecision`.
- The decision preserves the exact candidate identity.
- Actions are explicit: `ACCEPT`, `DEFER`, or `REJECT`.
- Confidence is bounded and remains distinct from certainty.
- The decision cannot grant learning-write authority or execution authority.
- No memory or learning storage is modified by this milestone.

## Boundary

```text
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
Learning Decision
↓
Learning / Memory Write Boundary
```

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.16 becomes VERIFIED / COMPLETE only after the user's local focused and core regression receipt passes.

Expected focused command:

```powershell
python -m unittest src.tools.tests.test_learning_decision -v
```

Expected regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```
