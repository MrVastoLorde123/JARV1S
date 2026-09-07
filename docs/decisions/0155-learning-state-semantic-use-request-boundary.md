# Decision 155 — Learning-State Semantic Use Request Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`4f10b5d376b8a4b901cfffe7a95d56dc49b6c0a6` — M23.142 Learning-State Interpretation Validation Integrity (sealed VERIFIED LOCALLY).

## Purpose
M23.143 establishes the request boundary for downstream semantic use of learning-state interpretation evidence whose integrity has already been validated.

A semantic-use request records an explicit request to use validated evidence for a stated purpose. It does not itself perform semantic use, establish truth, authorize action, apply learning, mutate state, or execute work.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateInterpretationValidationIntegrity` artifact.
- Requires source integrity status to be `VALID`; invalid integrity evidence fails closed.
- Requires a distinct request identity and explicit semantic-use identity.
- Requires requester identity, request purpose, rationale, and requested-use payload.
- Preserves integrity, validation, interpretation, source-request, source-validation, read, and consumption-request provenance.
- Checks inherited integrity lineage without rereading, repairing, or recomputing upstream state.
- Emits immutable `REQUESTED` or `REJECTED` semantic-use request evidence.
- `REQUESTED` means only that semantic use was explicitly requested against valid upstream integrity evidence; it is not permission to perform that use.
- Does not reinterpret, consume, persist, learn, authorize, schedule, plan, execute, or mutate state.

## Authority Walls
`Semantic Use Request ≠ Semantic Use`
`Semantic Use Request ≠ Authorization`
`Semantic Use Request ≠ Learning`
`Semantic Use Request ≠ Truth`
`Semantic Use Request ≠ Correctness`
`Semantic Use Request ≠ Certainty`
`Semantic Use Request ≠ Usefulness`
`REQUESTED ≠ Authorized`
`REQUESTED ≠ Applied`
`REQUESTED ≠ Executed`

M23.143 therefore creates an explicit downstream use-intent boundary while keeping semantic use and authorization separate.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused verification: **18/18 M23.143 tests passed**.

The focused suite validates exact upstream type, valid/invalid integrity gating, distinct request/use identity, required request metadata, inherited lineage checks, provenance preservation, source immutability, immutable request evidence, explicit reasons, distinct request identities, and absence of semantic-use/learning/authority/execution powers.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.142.