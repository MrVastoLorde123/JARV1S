# Decision 140 — Learning Proposal Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`1949db645427bc15f045cdfc86b4406dd384ac23` — M23.127 Learning Eligibility Boundary (sealed VERIFIED LOCALLY).

## Purpose
M23.128 establishes the bounded proposal boundary after learning eligibility.

The mechanism accepts one canonical `LearningStateExecutionLearningEligibility` artifact and constructs immutable evidence describing a candidate learning action. A proposal records intent and candidate change details for a future decision boundary; it does not decide, authorize, apply, or perform learning.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningEligibility` artifact.
- Requires eligibility to be explicitly `ELIGIBLE` before a proposal can be emitted.
- Requires explicit proposal identity, proposer identity, proposal purpose, and candidate change description.
- Preserves upstream eligibility, integrity, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Emits explicit `PROPOSED` or `REJECTED` status.
- Fails closed when eligibility is not valid or required proposal metadata is malformed.
- Preserves caller-supplied rationale and optional lineage without mutating the source eligibility artifact.
- Emits recursively immutable proposal evidence.
- Does not invoke a learner or model, mutate memory or policy, authorize learning, authorize execution, retry, schedule, plan, or apply changes.

## Authority Walls
`Learning Proposal ≠ Learning Eligibility`
`Learning Proposal ≠ Learning`
`Learning Proposal ≠ Learning Decision`
`Learning Proposal ≠ Learning Authorization`
`Learning Proposal ≠ Adaptation`
`Learning Proposal ≠ Truth`
`Learning Proposal ≠ Correctness`
`Learning Proposal ≠ Certainty`
`Learning Proposal ≠ Usefulness`
`Learning Proposal ≠ Execution Authorization`
`Learning Proposal ≠ Retry Authorization`
`Learning Proposal ≠ Model Update`
`Learning Proposal ≠ Memory Mutation`
`Learning Proposal ≠ Policy Mutation`
`PROPOSED ≠ Approved`
`PROPOSED ≠ Applied`
`REJECTED ≠ Repair Required`
`Eligible ≠ Automatic Learning`

M23.128 makes candidate learning intent explicit while preserving the boundary that proposal generation is not a decision or an application.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal`

## Verification Plan
Focused tests cover exact source type, required proposal metadata, ELIGIBLE/REJECTED eligibility handling, fail-closed proposal rejection, upstream provenance and fingerprint preservation, caller rationale and lineage preservation, recursive immutability, source non-mutation, deterministic construction, proposal semantics, and absence of learning, adaptation, decision, authorization, execution, retry, scheduling, planning, model, memory, and policy powers.

Local verification will be recorded here after the focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.127.
