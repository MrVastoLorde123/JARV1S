# Decision 177 — Learning-State Transition Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`6d268e7c9c593546a9cfd4312fdd09c195db97c2` — M23.164 Learning-State Evidence.

## Purpose
M23.165 establishes a bounded learning-state transition-formulation boundary after recorded learning-state evidence.

This boundary explicitly describes a candidate state transition. It does not mutate durable state, persist state, authorize execution, authorize retry, schedule work, execute work, invoke a learner, update a model, mutate memory or policy, or establish truth/correctness/certainty/usefulness.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateEvidence` artifact.
- Requires a distinct transition identity and explicit state key, before-state, after-state, actor, purpose, and rationale.
- Requires the upstream evidence to be `RECORDED` with internally consistent anchored evidence/integrity/application/source-integrity lineage.
- A valid recorded evidence artifact produces `FORMULATED`; rejected or tampered evidence fails closed as `REJECTED`.
- Computes a deterministic SHA-256 transition fingerprint over the transition identity, state key, before-state, after-state, evidence identity, integrity identity, and proposed change.
- Preserves the complete evidence provenance chain without mutating the source evidence.
- Recursively freezes state values, rationale, evidence payload, and lineage.
- `FORMULATED` means a transition record was formed; it does not mean the state was changed.

## Authority Walls
`State Evidence ≠ State Transition`
`FORMULATED ≠ Applied`
`FORMULATED ≠ Persisted`
`FORMULATED ≠ Executed`
`FORMULATED ≠ Learned`
`FORMULATED ≠ Authorized`
`FORMULATED ≠ True`
`FORMULATED ≠ Correct`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation`

## Verification
Focused local verification:
`python -m unittest src.core.tests.test_learning_state_execution_learning_state_transition -v`

Result:
`Ran 19 tests in 0.013s`
`OK`

## Atomicity
Exactly **1 commit / 3 intended files** from M23.164. No merge is implied by this decision.
