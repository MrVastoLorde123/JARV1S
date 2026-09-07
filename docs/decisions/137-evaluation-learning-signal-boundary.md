# Decision 137 — Evaluation → Learning Signal Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`fa64d69105c514e9a0befaec675a378f1789f4df` — M23.124 Execution Feedback → Evaluation Boundary.

## Purpose
M23.125 establishes the bounded learning-signal boundary after evaluation.

The mechanism converts one explicit evaluation judgment into immutable learning-signal evidence. A learning signal is a signal for a later learning mechanism; it is not learning itself, truth, adaptation, authorization, retry permission, execution, memory mutation, or policy change.

## Contract
- Accepts exactly one canonical `LearningStateExecutionEvaluation` artifact.
- Requires explicit signal identity, signal kind, and signal purpose.
- Preserves the evaluation objective, judgment, context, feedback, observed consequence, execution evidence, provenance, and fingerprints.
- Requires the caller to explicitly classify the learning signal as `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `UNKNOWN`; the boundary does not infer a signal from free-form judgment content.
- Emits recursively immutable learning-signal evidence.
- Does not invoke a learner or model and does not update learning state.
- Does not establish truth, correctness, certainty, or usefulness.
- Does not authorize execution, retry, scheduling, planning, or policy mutation.

## Authority Walls
`Evaluation ≠ Learning Signal`
`Learning Signal ≠ Learning`
`Learning Signal ≠ Truth`
`Learning Signal ≠ Correctness`
`Learning Signal ≠ Certainty`
`Learning Signal ≠ Usefulness`
`Learning Signal ≠ Adaptation`
`Learning Signal ≠ Retry Authorization`
`Learning Signal ≠ Authorization`
`Learning Signal ≠ Execution`
`Learning Signal ≠ Scheduling`
`Learning Signal ≠ Planning`
`Learning Signal ≠ Model Update`
`Learning Signal ≠ Memory Mutation`
`Learning Signal ≠ Policy Mutation`
`Signal Kind ≠ World Truth`
`Evaluation Judgment ≠ Automatic Learning`

M23.125 creates the explicit handoff from evaluation into the learning pipeline while keeping learning itself downstream.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → (future signal-integrity boundary)`

## Verification Plan
Focused tests cover exact source type, explicit signal classification, identity/purpose requirements, provenance preservation, evaluation-judgment preservation, observed execution evidence preservation, recursive immutability, source non-mutation, deterministic construction, absence of learner/model invocation, and absence of truth, adaptation, authorization, retry, execution, scheduling, planning, memory, or policy powers.

Local verification results:
- Focused M23.125 learning-signal suite: **13/13 PASS**
- Focused M23.124 execution-feedback evaluation suite: **12/12 PASS**
- Focused M23.123 execution-feedback suite: **14/14 PASS**
- Focused M23.122 execution-outcome suite: **16/16 PASS**
- Full `src/core/tests` regression suite: **1915/1915 PASS**

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.124.
