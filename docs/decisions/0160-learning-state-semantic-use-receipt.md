# Decision 160 — Learning-State Semantic Use Receipt

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`ca0397578630aa7448b2d70d74603f29519487fc` — M23.147 Learning-State Semantic Use Handoff (sealed VERIFIED LOCALLY).

## Purpose
M23.148 establishes a bounded receipt boundary for a semantic-use handoff that has been accepted by an explicitly identified downstream recipient.

The receipt records that a specific handoff was received at the declared downstream boundary. Receipt does not itself consume, apply, authorize, execute, schedule, persist, reinterpret, or establish truth about the handed-off evidence.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateSemanticUseHandoff` artifact.
- Requires handoff status `HANDED_OFF`; rejected handoffs fail closed.
- Requires a distinct receipt identity and explicit recipient, purpose, and rationale.
- Preserves immediate handoff identity separately from integrity, validation, semantic-use, source-request, source-validation, interpretation, read, and consumption-request provenance.
- Checks the handoff artifact's anchored lineage without rereading or repairing upstream artifacts.
- Preserves inherited upstream provenance exactly as supplied by the handoff artifact; it does not independently re-prove upstream values.
- Produces immutable `RECEIVED` or `REJECTED` receipt evidence.
- `RECEIVED` means only that the declared downstream recipient structurally acknowledged receipt of the handoff; it is not consumption, application, authorization, execution, truth, correctness, certainty, or usefulness.
- Performs no semantic reinterpretation, learning, durable-state mutation, authorization, scheduling, planning, persistence, policy mutation, or execution.

## Authority Walls
`Semantic Use Receipt ≠ Semantic Use Handoff`
`Semantic Use Receipt ≠ Semantic Use Consumption`
`Receipt ≠ Authorization`
`Receipt ≠ Execution`
`Receipt ≠ Learning`
`Receipt ≠ Truth`
`Receipt ≠ Correctness`
`Receipt ≠ Certainty`
`Receipt ≠ Usefulness`
`RECEIVED ≠ Consumed`
`RECEIVED ≠ Applied`
`RECEIVED ≠ Executed`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused local verification completed:

```text
python -m unittest src.core.tests.test_learning_state_execution_learning_state_semantic_use_receipt -v
Ran 21 tests in 0.010s
OK
```

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.147.
