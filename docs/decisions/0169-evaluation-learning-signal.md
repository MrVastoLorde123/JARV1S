# Decision 169 — Evaluation → Learning Signal

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`f039a50d2f5ac68e1345cdf32a1f418151eb5231` — M23.156 Execution Feedback → Evaluation (sealed VERIFIED LOCALLY).

## Purpose
M23.157 establishes the bounded learning-signal boundary after execution-feedback evaluation.

A learning signal converts one evaluated execution-feedback artifact into explicit signal evidence for a later learning mechanism. The boundary does not itself learn, update a model, mutate memory or policy, authorize execution or retry, or establish truth.

## Contract
- Accepts exactly one canonical `LearningStateExecutionEvaluation` artifact.
- Requires evaluation status `EVALUATED`; rejected evaluation fails closed.
- Requires a distinct signal identity, explicit signal kind, signal purpose, and signal context.
- Requires the caller to explicitly classify the signal as `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `UNKNOWN`; classification is not inferred from the evaluation judgment.
- Preserves evaluation identity, objective, judgment, context, feedback, observed outcome, execution target, authorization scope, and all inherited upstream provenance.
- Checks the evaluation artifact's anchored lineage without rereading or repairing upstream artifacts.
- Produces recursively immutable learning-signal evidence.
- `signal kind` is an explicit downstream classification, not truth, certainty, correctness, or automatic learning.
- Performs no learner invocation, model update, adaptation, execution, retry authorization, scheduling, persistence, policy mutation, or durable-state mutation.

## Authority Walls
`Evaluation ≠ Learning Signal`
`Learning Signal ≠ Learning`
`Learning Signal ≠ Truth`
`Learning Signal ≠ Correctness`
`Learning Signal ≠ Certainty`
`Learning Signal ≠ Usefulness`
`Learning Signal ≠ Adaptation`
`Learning Signal ≠ Retry Authorization`
`Learning Signal ≠ Execution Authorization`
`Learning Signal ≠ Execution`
`Learning Signal ≠ Model Update`
`Learning Signal ≠ Memory Mutation`
`Learning Signal ≠ Policy Mutation`
`Signal Kind ≠ World Truth`
`EVALUATED ≠ Learned`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal`

## Verification
Local verification results:
- Focused M23.157 evaluation-learning-signal suite: **23/23 PASS**

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.156.
