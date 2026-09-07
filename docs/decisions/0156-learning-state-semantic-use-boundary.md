# Decision 156 — Learning-State Semantic Use Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`b42b8fa5276026aaf587e503a428f63175742566` — M23.143 Learning-State Semantic Use Request (sealed VERIFIED LOCALLY).

## Purpose
M23.144 establishes the semantic-use boundary for an explicitly requested downstream use of learning-state interpretation evidence.

Semantic use performs only the bounded, explicit use described by the request. It does not authorize external action, establish semantic truth, apply learning, mutate durable state, or execute work.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateSemanticUseRequest` artifact.
- Requires request status to be `REQUESTED`; rejected requests fail closed.
- Requires a distinct semantic-use identity and explicit consumer identity, purpose, and rationale.
- Preserves the immediate semantic-use request identity separately from its inherited `source_request_id` provenance.
- Preserves integrity, validation, interpretation, source-request, source-validation, read, and consumption-request provenance.
- Checks inherited request lineage without rereading or repairing upstream evidence.
- Produces immutable `USED` or `REJECTED` semantic-use evidence.
- `USED` means only that the requested semantic use was structurally performed within this boundary; it is not authorization or proof of truth, correctness, certainty, or usefulness.
- Does not authorize external actions, apply learning, persist state, schedule work, plan execution, invoke executors, or mutate policy or memory.

## Authority Walls
`Semantic Use ≠ Semantic Use Request`
`Semantic Use ≠ Authorization`
`Semantic Use ≠ Learning`
`Semantic Use ≠ Truth`
`Semantic Use ≠ Correctness`
`Semantic Use ≠ Certainty`
`Semantic Use ≠ Usefulness`
`USED ≠ Authorized`
`USED ≠ Applied`
`USED ≠ Executed`

M23.144 therefore performs bounded downstream semantic use while preserving the separate authorization and execution boundaries.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused local verification: **19/19 PASS**

Command:
`python -m unittest src.core.tests.test_learning_state_execution_learning_state_semantic_use -v`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.143.