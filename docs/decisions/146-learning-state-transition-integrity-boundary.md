# Decision 146 — Learning-State Transition Integrity Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`a4cc85bd1eaf82ef86e120eaf33c8429d93398b7` — M23.133 Learning-State Transition (sealed VERIFIED LOCALLY).

## Purpose
M23.134 establishes the bounded integrity boundary for a formulated learning-state transition.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningStateTransition` artifact and validates its structural identity, preserved lineage, explicit state-change fields, and deterministic transition fingerprint. It emits a distinct immutable integrity artifact describing whether the transition remains internally coherent. Integrity validation does not apply the transition, mutate durable state, execute work, authorize execution or retry, or repair invalid evidence.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateTransition` artifact.
- Requires the source transition to be `FORMULATED`; rejected transitions fail closed.
- Requires a distinct integrity identity.
- Checks transition identity, evidence lineage, explicit state key and before/after state values, preserved transition lineage, and SHA-256 transition fingerprint integrity.
- Recomputes the expected transition fingerprint from the transition's immutable inputs without mutating the source transition.
- Emits explicit `VALID` or `INVALID` integrity status.
- Preserves transition, evidence, application, decision, proposal, eligibility, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Preserves caller-supplied reasons and optional lineage.
- Emits recursively immutable integrity evidence, including malformed fingerprints when recording `INVALID` status.
- Does not repair invalid transition data.
- Does not mutate or persist learning state, execute work, authorize execution or retry, schedule, plan, invoke a learner or executor, or mutate model, memory, policy, or external systems.

## Authority Walls
`Transition Integrity ≠ Transition`
`Transition Integrity ≠ Durable-State Mutation`
`Transition Integrity ≠ Execution`
`Transition Integrity ≠ Execution Authorization`
`Transition Integrity ≠ Retry Authorization`
`Transition Integrity ≠ Learning`
`Transition Integrity ≠ Repair`
`Transition Integrity ≠ Truth`
`Transition Integrity ≠ Correctness`
`Transition Integrity ≠ Certainty`
`Transition Integrity ≠ Usefulness`
`VALID ≠ Applied`
`VALID ≠ Persisted`
`INVALID ≠ Automatically Repaired`

M23.134 makes the integrity checkpoint explicit: a formally described state transition must remain structurally and cryptographically coherent before any later boundary can consume it, while integrity itself carries no authority to mutate state or execute work.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity`

## Verification Plan
Focused tests cover exact source type, formulated/rejected handling, distinct integrity identity, transition fingerprint recomputation, lineage consistency, provenance preservation, malformed fingerprint reporting without repair, recursively immutable evidence, reason preservation, source non-mutation, deterministic validation, immutable integrity artifacts, and absence of state mutation, persistence, execution, retry, scheduling, planning, learner, executor, model, memory, policy, truth, correctness, certainty, and usefulness powers.

Local verification will be recorded here after focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.133.
