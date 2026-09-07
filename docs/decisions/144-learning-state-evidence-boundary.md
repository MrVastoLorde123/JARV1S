# Decision 144 — Learning-State Evidence Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`bd086463bd28a942716111cf6a86851c253b3a2d` — M23.131 Learning Proposal Application Integrity (sealed VERIFIED LOCALLY).

## Purpose
M23.132 establishes the bounded learning-state evidence boundary after application-integrity validation.

The mechanism accepts one canonical `LearningStateExecutionLearningProposalApplicationIntegrity` artifact and records immutable evidence describing the candidate learning-state effect represented by that application. Evidence is a record of what was presented for state evaluation; it is not a state transition, truth claim, execution result, authorization, or memory mutation.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalApplicationIntegrity` artifact.
- Requires explicit evidence identity, collector identity, evidence purpose, and evidence rationale.
- Requires source integrity to be `VALID` and internally consistent before evidence may be recorded as `RECORDED`; invalid or internally inconsistent integrity fails closed into explicit `REJECTED` evidence.
- Preserves application, decision, proposal, eligibility, integrity, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Preserves application status as evidence.
- Records caller-supplied evidence payload, reasons, and lineage without mutating source integrity or application artifacts.
- Emits recursively immutable evidence.
- Does not transition learning state, persist state, execute work, authorize execution or retry, schedule, plan, invoke an executor or learner, repair invalid evidence, or mutate model, memory, or policy.

## Authority Walls
`Learning-State Evidence ≠ Learning-State Transition`
`Learning-State Evidence ≠ Learning`
`Learning-State Evidence ≠ Truth`
`Learning-State Evidence ≠ Correctness`
`Learning-State Evidence ≠ Certainty`
`Learning-State Evidence ≠ Usefulness`
`Learning-State Evidence ≠ Authorization`
`Learning-State Evidence ≠ Execution`
`Learning-State Evidence ≠ Retry Authorization`
`Learning-State Evidence ≠ Persistence Mutation`
`RECORDED ≠ Applied`
`RECORDED ≠ Transitioned`
`RECORDED ≠ Executed`
`REJECTED ≠ Automatically Repaired`

M23.132 makes the state-evidence checkpoint explicit: application integrity can be converted into bounded evidence describing a candidate state effect only when the integrity artifact remains internally consistent, while evidence remains observational and non-mutating until a later transition boundary.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence`

## Verification
- M23.132 focused: previously recorded 14/14; regression uncovered 1 fail in `test_invalid_integrity_fails_closed` because internally tampered integrity lineage was still accepted as `RECORDED`.
- M23.131 focused: 15/15 passed
- M23.130 focused: 10/10 passed
- M23.129 focused: 10/10 passed
- M23.128 focused: 10/10 passed
- M23.127 focused: 11/11 passed
- M23.126 focused: 15/15 passed
- M23.125 focused: 13/13 passed
- M23.124 focused: 12/12 passed

The M23.132 production boundary has been corrected to fail closed when the validated integrity artifact's application or decision lineage no longer matches its preserved lineage evidence. Local verification remains pending until the focused suite and regression block are rerun successfully.

The full repository discovery run remains outside the scope of this milestone because its known baseline failures include unrelated database bootstrap/environment errors and legacy filesystem error-code expectations.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.131.
