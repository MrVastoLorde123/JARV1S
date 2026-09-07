# Decision 142 — Learning Proposal Application Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`4e292e40e045ee526608d9c6f0fcc5252154e3d6` — M23.129 Learning Proposal Decision (sealed VERIFIED LOCALLY).

## Purpose
M23.130 establishes the bounded application boundary after a learning proposal decision.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningProposalDecision` artifact and constructs immutable evidence that an approved proposal has entered an application attempt. The boundary records application identity, actor, purpose, rationale, and optional application evidence without granting execution authority or silently performing unrelated work.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalDecision` artifact.
- Requires the source decision to be explicitly `APPROVED` before an application attempt may be recorded.
- Requires explicit application identity, applier identity, application purpose, and application rationale.
- Emits explicit `ATTEMPTED` or `REJECTED` status.
- Fails closed when the decision is not approved or required application metadata is malformed.
- Preserves upstream decision, proposal, eligibility, integrity, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Preserves optional application evidence and caller-supplied reasons without mutating the source decision.
- Emits recursively immutable application evidence.
- Does not authorize execution, authorize retry, schedule work, plan work, invoke an executor, or mutate unrelated policy or memory state.

## Authority Walls
`Learning Proposal Application ≠ Learning Proposal Decision`
`Learning Proposal Application ≠ Learning Authorization`
`Learning Proposal Application ≠ Execution Authorization`
`Learning Proposal Application ≠ Execution`
`Learning Proposal Application ≠ Retry Authorization`
`Learning Proposal Application ≠ Scheduling`
`Learning Proposal Application ≠ Planning`
`Learning Proposal Application ≠ Truth`
`Learning Proposal Application ≠ Correctness`
`Learning Proposal Application ≠ Certainty`
`Learning Proposal Application ≠ Usefulness`
`ATTEMPTED ≠ Executed`
`ATTEMPTED ≠ Execution Authorized`
`REJECTED ≠ Repair Required`

M23.130 makes the application boundary explicit: an approved learning decision can enter an application attempt, but that artifact does not become an execution permission or an executor invocation.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application`

## Verification Plan
Focused tests cover exact source type, approved/rejected decision handling, fail-closed rejection, required application metadata, upstream provenance and fingerprint preservation, recursive immutability, source non-mutation, deterministic construction, application semantics, optional evidence/reason preservation, and absence of execution, retry, scheduling, planning, executor, model, memory, and policy powers.

Local verification will be recorded here after focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.129.
