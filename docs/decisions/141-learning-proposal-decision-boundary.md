# Decision 141 — Learning Proposal Decision Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`24a591d2bc1e8506967eb18353a206cb40f1be45` — M23.128 Learning Proposal Boundary (sealed VERIFIED LOCALLY).

## Purpose
M23.129 establishes the bounded decision boundary after learning proposal generation.

The mechanism evaluates one canonical `LearningStateExecutionLearningProposal` artifact and emits an explicit decision describing whether the proposal may proceed to a future application boundary. The decision layer does not perform learning, apply a proposed change, mutate a model, mutate memory or policy, or authorize execution.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposal` artifact.
- Requires proposal status to be explicitly `PROPOSED` before approval can be emitted.
- Requires explicit decision identity, decision-maker identity, decision purpose, and decision rationale.
- Emits explicit `APPROVED` or `REJECTED` status.
- Fails closed when proposal status is not `PROPOSED` or required decision metadata is malformed.
- Preserves upstream proposal, eligibility, integrity, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Preserves caller-supplied reasons and optional lineage without mutating the source proposal.
- Emits recursively immutable decision evidence.
- Does not perform, authorize, or imply learning, adaptation, model update, memory mutation, policy mutation, execution, retry, scheduling, or planning.

## Authority Walls
`Learning Proposal Decision ≠ Learning Proposal`
`Learning Proposal Decision ≠ Learning`
`Learning Proposal Decision ≠ Learning Application`
`Learning Proposal Decision ≠ Learning Authorization`
`Learning Proposal Decision ≠ Adaptation`
`Learning Proposal Decision ≠ Truth`
`Learning Proposal Decision ≠ Correctness`
`Learning Proposal Decision ≠ Certainty`
`Learning Proposal Decision ≠ Usefulness`
`Learning Proposal Decision ≠ Execution Authorization`
`Learning Proposal Decision ≠ Retry Authorization`
`Learning Proposal Decision ≠ Model Update`
`Learning Proposal Decision ≠ Memory Mutation`
`Learning Proposal Decision ≠ Policy Mutation`
`APPROVED ≠ Applied`
`APPROVED ≠ Learned`
`APPROVED ≠ Executed`
`REJECTED ≠ Repair Required`

M23.129 makes the review/decision point explicit: a proposed learning change can be accepted for a future application boundary, but the decision itself is neither learning nor application.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision`

## Verification Plan
Focused tests cover exact source type, required decision metadata, PROPOSED/REJECTED proposal handling, fail-closed rejection, upstream provenance and fingerprint preservation, explicit decision rationale, recursive immutability, source non-mutation, deterministic construction, decision semantics, and absence of learning, application, authorization, execution, retry, scheduling, planning, model, memory, and policy powers.

Local verification will be recorded here after the focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.128.
