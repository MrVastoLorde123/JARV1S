# Decision 161 — Learning-State Semantic Use Consumption

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`57a1f04780975a890932f48efd3d42e57fff545b` — M23.148 Learning-State Semantic Use Receipt (sealed VERIFIED LOCALLY).

## Purpose
M23.149 establishes a bounded consumption boundary for a semantic-use receipt that has been acknowledged by an explicitly identified recipient.

Consumption records that the received semantic-use handoff was consumed at the declared downstream boundary for the stated purpose. Consumption does not itself authorize, execute, schedule, persist, reinterpret, learn, or establish truth about the consumed evidence.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateSemanticUseReceipt` artifact.
- Requires receipt status `RECEIVED`; rejected receipts fail closed.
- Requires a distinct consumption identity and explicit consumer, purpose, and rationale.
- Preserves immediate receipt identity separately from handoff, integrity, validation, semantic-use, source-request, source-validation, interpretation, read, and consumption-request provenance.
- Checks the receipt artifact's anchored lineage without rereading or repairing upstream artifacts.
- Preserves inherited upstream provenance exactly as supplied by the receipt artifact; it does not independently re-prove upstream values.
- Produces immutable `CONSUMED` or `REJECTED` consumption evidence.
- `CONSUMED` means only that the received semantic-use evidence was structurally consumed at the declared downstream boundary; it is not application, authorization, execution, truth, correctness, certainty, or usefulness.
- Performs no semantic reinterpretation, learning, durable-state mutation, authorization, scheduling, planning, persistence, policy mutation, or execution.

## Authority Walls
`Semantic Use Consumption ≠ Semantic Use Receipt`
`Semantic Use Consumption ≠ Downstream Semantic Handling`
`Consumption ≠ Authorization`
`Consumption ≠ Execution`
`Consumption ≠ Learning`
`Consumption ≠ Truth`
`Consumption ≠ Correctness`
`Consumption ≠ Certainty`
`Consumption ≠ Usefulness`
`CONSUMED ≠ Applied`
`CONSUMED ≠ Authorized`
`CONSUMED ≠ Executed`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused local verification completed:

```text
python -m unittest src.core.tests.test_learning_state_execution_learning_state_semantic_use_consumption -v
Ran 22 tests in 0.012s
OK
```

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.148.