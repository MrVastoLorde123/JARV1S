# M22.17 — Learning Write Proposal Boundary

## Purpose

Establish an inert boundary between an accepted `LearningDecision` and any later learning-state or memory mutation.

## Contract

- `LearningWriteProposalService` consumes an explicit `LearningWriteProposalContext`.
- The context binds the exact `LearningDecision` to the exact source `LearningCandidate`.
- Only `ACCEPT` decisions may produce a `LearningWriteProposal`.
- `DEFER` and `REJECT` produce no proposal.
- The proposal preserves decision/candidate/execution/handoff identity.
- The proposal carries an explicit `LearningWriteDomain` and immutable payload.
- Candidate evidence and provenance remain preserved and immutable.
- Proposal confidence cannot exceed source decision or candidate confidence.
- The proposal cannot grant authority, permit execution, or claim a memory mutation.

## Learning domains

The boundary supports learning beyond memory by distinguishing:

`EPISODIC, SEMANTIC, PROCEDURAL, PREFERENCE, FAILURE_OUTCOME, BELIEF, PREDICTIVE, META`

## Boundary

```text
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
LearningDecisionService
↓
LearningDecision
↓
LearningWriteProposalService
↓
LearningWriteProposal
↓
Learning / Memory Write Policy
↓
Learning State / Memory Mutation
```

## Authority walls

- Learning Decision ≠ Learning Write Proposal
- Learning Write Proposal ≠ Learning Write
- Learning Write Proposal ≠ Memory Mutation
- Learning ≠ Authority
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Candidate Evidence ≠ Truth
- Confidence ≠ Certainty
- Learning Domain ≠ Memory Domain

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Expected focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_proposal -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```
