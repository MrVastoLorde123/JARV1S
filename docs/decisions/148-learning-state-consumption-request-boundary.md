# Decision 148 — Learning-State Consumption Request Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`05843446a65c04ab8cac5f5cfb6290e589fe92c9` — M23.135 Learning-State Validation (focused 18/18 and regression chain green).

## Purpose
M23.136 establishes the bounded request boundary between validated learning-state evidence and the later durable-state read/consumption path.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningStateValidation` artifact with `VALIDATED` status and forms an explicit immutable consumption request. The request records who is asking to consume validated state, what state is requested, and why. A request is intent-to-consume evidence only; it does not read storage, return durable state, mutate state, persist changes, execute work, authorize execution or retry, interpret meaning, or establish truth.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateValidation` artifact.
- Requires the source validation status to be `VALIDATED`; rejected validation fails closed.
- Requires source validation lineage to agree with its own validation, integrity, transition, and evidence identities.
- Requires an explicit, distinct consumption-request identity.
- Preserves state key, before/after state evidence, fingerprints, and complete upstream provenance.
- Records explicit requester identity, request purpose, requested scope, and rationale.
- Preserves caller-supplied reasons and optional lineage without mutating the source validation artifact.
- Emits recursively immutable request evidence.
- Emits `REQUESTED` or `REJECTED` explicitly.
- `REQUESTED` means a bounded downstream read/consumption operation may be considered; it does not perform that operation.
- Does not read durable state, persist state, mutate learning state, apply learning, execute work, authorize execution or retry, schedule, plan, repair, invoke a learner or executor, mutate model/memory/policy, or infer truth/correctness/certainty/usefulness.

## Authority Walls
`Consumption Request ≠ Durable-State Read`
`Consumption Request ≠ Learning-State Consumption`
`Consumption Request ≠ Durable-State Mutation`
`Consumption Request ≠ Execution`
`Consumption Request ≠ Execution Authorization`
`Consumption Request ≠ Retry Authorization`
`Consumption Request ≠ Learning`
`Consumption Request ≠ Repair`
`REQUESTED ≠ Read`
`REQUESTED ≠ Consumed`
`REQUESTED ≠ Applied`
`REQUESTED ≠ Persisted`
`REQUESTED ≠ Executed`
`Request ≠ Truth`
`Request ≠ Correctness`
`Request ≠ Certainty`
`Request ≠ Usefulness`

M23.136 makes the request boundary explicit: validated state may be named and requested for downstream consumption without silently granting the request authority to read storage, interpret the state, or perform any mutation or execution.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
- M23.136 focused: **36/36 passed** (18 M23.135 regression tests + 18 M23.136 boundary tests)
- M23.135 focused: **18/18 passed**
- M23.134 focused: **16/16 passed**
- M23.133 focused: **14/14 passed**
- M23.132 regression: **14/14 passed**
- M23.131 regression: **15/15 passed**
- M23.130 regression: **10/10 passed**
- M23.129 regression: **10/10 passed**
- M23.128 regression: **10/10 passed**
- M23.127 regression: **11/11 passed**
- M23.126 regression: **15/15 passed**
- M23.125 regression: **13/13 passed**
- M23.124 regression: **12/12 passed**

Focused verification covers exact source type, validated/rejected handling, source lineage consistency, distinct request identity, required request metadata, state-scope preservation, provenance and fingerprint preservation, reason and lineage preservation, recursive immutability, source non-mutation, deterministic request formation, immutable request artifacts, explicit `REQUESTED`/`REJECTED` status, and absence of read, consumption, mutation, persistence, learning, interpretation, execution, authorization, retry, scheduling, planning, repair, model, memory, policy, truth, correctness, certainty, and usefulness powers.

The regression chain confirms M23.135 remains green while M23.136 consumes its validated artifact contract. The full repository discovery run remains outside the scope of this milestone because its known baseline failures include unrelated database bootstrap/environment errors and legacy filesystem error-code expectations.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.135.
