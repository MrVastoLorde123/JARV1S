# Decision 164 — Execution Admission / Authorization

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`6a7e7942c1569d2d3d7428e27ab1cd1f65af60cc` — M23.151 Execution Eligibility (sealed VERIFIED LOCALLY).

## Purpose
M23.152 establishes the bounded boundary where an eligible execution request may be admitted and explicitly authorized for one declared execution target and scope.

Admission / authorization records a constrained grant to proceed to an execution-attempt boundary. It does not itself invoke, schedule, retry, or execute work.

## Contract
- Accepts exactly one canonical `LearningStateExecutionEligibility` artifact.
- Requires eligibility status `ELIGIBLE`; ineligible evidence fails closed.
- Requires a distinct admission identity and explicit execution target, authorization scope, authority basis, purpose, and rationale.
- Preserves immediate eligibility identity separately from handling, consumption, receipt, handoff, integrity, validation, semantic-use, source-request, source-validation, interpretation, read, and consumption-request provenance.
- Checks the eligibility artifact's anchored lineage without rereading or repairing upstream artifacts.
- Produces immutable `ADMITTED` or `REJECTED` authorization evidence.
- `ADMITTED` means only that execution has been explicitly authorized within the declared target and scope; it is not an execution attempt, execution outcome, learning event, truth claim, correctness claim, certainty claim, or usefulness claim.
- Authorization is scoped to the recorded execution target and scope and must not silently expand them.
- Performs no execution, retry, scheduling, planning, persistence, learner invocation, executor invocation, durable-state mutation, or policy mutation.

## Authority Walls
`Execution Admission / Authorization ≠ Execution Attempt`
`Authorization ≠ Execution`
`Authorization ≠ Learning`
`Authorization ≠ Truth`
`Authorization ≠ Correctness`
`Authorization ≠ Certainty`
`Authorization ≠ Usefulness`
`ADMITTED ≠ Executed`
`ADMITTED ≠ Succeeded`
`ADMITTED ≠ Learned`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused local verification completed:

```text
python -m unittest src.core.tests.test_learning_state_execution_learning_state_execution_admission_authorization -v
Ran 30 tests in 0.009s
OK
```

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.151.