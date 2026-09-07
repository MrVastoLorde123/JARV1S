# Decision 145 — Learning-State Transition Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`a3c47af894a4cc9315ea7106310ad86442bf86cf` — M23.132 Learning-State Evidence (sealed VERIFIED LOCALLY).

## Purpose
M23.133 establishes the bounded learning-state transition boundary after recorded learning-state evidence.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningStateEvidence` artifact with `RECORDED` status and forms an explicit immutable transition artifact describing the requested `before → after` state change. The transition is a formal state-change record only; it does not mutate durable state, execute work, authorize execution, authorize retry, schedule work, or invoke an executor.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateEvidence` artifact.
- Requires the source evidence to be `RECORDED`; rejected evidence fails closed.
- Requires explicit transition identity, transition actor identity, purpose, rationale, and state-before/state-after values.
- Preserves evidence, integrity, application, decision, proposal, eligibility, signal, evaluation, feedback, outcome, execution, and fingerprint provenance.
- Computes a deterministic SHA-256 transition fingerprint from the explicit transition identity, state key, before/after state values, source evidence identity, source integrity identity, and proposed change.
- Preserves caller-supplied reasons and lineage without mutating the source evidence.
- Emits recursively immutable transition data.
- Represents a candidate state transition without persisting or mutating durable learning state.
- Does not execute work, authorize execution or retry, schedule, plan, invoke a learner or executor, repair invalid evidence, or mutate model, memory, policy, or external systems.

## Authority Walls
`Learning-State Transition ≠ Durable-State Mutation`
`Learning-State Transition ≠ Execution`
`Learning-State Transition ≠ Execution Authorization`
`Learning-State Transition ≠ Retry Authorization`
`Learning-State Transition ≠ Learning`
`Learning-State Transition ≠ Truth`
`Learning-State Transition ≠ Correctness`
`Learning-State Transition ≠ Certainty`
`Learning-State Transition ≠ Usefulness`
`RECORDED ≠ Persisted`
`RECORDED ≠ Executed`
`REJECTED ≠ Automatically Repaired`

M23.133 is the explicit bridge from state evidence to a formally described state change while preserving the authority wall: describing a transition is not the same operation as mutating durable state or executing external work.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition`

## Verification Plan
Focused tests cover exact source type, recorded/rejected handling, required transition metadata, explicit before/after states, deterministic transition fingerprints, complete provenance preservation, recursive immutability, reason and lineage preservation, source non-mutation, immutable transition artifacts, and absence of durable-state mutation, persistence, execution, retry, scheduling, planning, learner, executor, model, memory, policy, truth, correctness, certainty, and usefulness powers.

Local verification will be recorded here after focused and regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.132.
