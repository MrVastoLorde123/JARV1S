# Decision 143 — Learning Proposal Application Integrity Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`290805398592db5269f06051ece1cffaf397537d` — M23.130 Learning Proposal Application (verified by focused and regression suites).

## Purpose
M23.131 establishes the bounded integrity boundary after a learning proposal application attempt.

The mechanism validates the structural and provenance integrity of one canonical `LearningStateExecutionLearningProposalApplication` artifact and emits a distinct integrity evidence artifact. Integrity validation records whether the application evidence is structurally coherent; it does not repair the application, execute the proposed change, grant authority, or infer truth or correctness.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalApplication` artifact.
- Requires an explicit integrity identity distinct from the application identity.
- Preserves the application, decision, proposal, eligibility, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Preserves the application's explicit `ATTEMPTED`/`REJECTED` status as evidence rather than converting it into execution authority.
- Checks required identities, application/decision lineage consistency, fingerprint shape, and caller-supplied reasons.
- Emits explicit `VALID` or `INVALID` integrity status.
- Fails closed on wrong source type or malformed required integrity metadata.
- Preserves caller-supplied reasons and optional lineage without mutating the source application artifact.
- Emits recursively immutable integrity evidence, including malformed source values when recording `INVALID` status.
- Does not repair, apply, execute, authorize execution, authorize retry, schedule work, plan work, invoke an executor, mutate memory, or mutate policy.

## Authority Walls
`Application Integrity ≠ Application`
`Application Integrity ≠ Learning`
`Application Integrity ≠ Repair`
`Application Integrity ≠ Execution Authorization`
`Application Integrity ≠ Execution`
`Application Integrity ≠ Retry Authorization`
`Application Integrity ≠ Scheduling`
`Application Integrity ≠ Planning`
`Application Integrity ≠ Truth`
`Application Integrity ≠ Correctness`
`Application Integrity ≠ Certainty`
`Application Integrity ≠ Usefulness`
`VALID ≠ Applied`
`VALID ≠ Executed`
`INVALID ≠ Automatically Repaired`

M23.131 makes the application-integrity checkpoint explicit: an application attempt becomes integrity evidence before later state-evidence and transition boundaries, while integrity itself has no execution power.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity`

## Verification Plan
Focused tests cover exact source type, integrity identity, valid/invalid application handling, lineage validation, upstream provenance, distinct integrity identity, fingerprint preservation, recursive immutability, reason preservation, source non-mutation, artifact immutability, deterministic construction, fail-closed fingerprint reporting, preserved application status, and absence of learning, repair, authorization, execution, retry, scheduling, planning, executor, model, memory, and policy powers.

Local verification will be recorded here after focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.130.
