# Decision 115 — Learning-State Integrity Validation Boundary

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`4e2d33f60afd9df94212d695f95358bc5ccd3257` — M23.102 Learning-State Integrity Import Compatibility Contract.

## Purpose
M23.103 establishes the next bounded consumer boundary after M23.99 transition integrity: a caller can determine whether learning-state integrity evidence is structurally acceptable for downstream consumption.

The validator accepts exactly one canonical learning-state transition integrity artifact and emits immutable validation evidence. Consumption eligibility requires both `VALID` transition integrity and a `PERSISTED` transition status. The validator does not read or mutate a durable store and does not invoke learning.

## Contract
- Consumes exactly one `LearningStateTransitionIntegrity` artifact through the canonical module surface.
- Requires integrity status `VALID` and transition status `PERSISTED` for an `ACCEPTED` result.
- Returns `REJECTED` for validly formed but non-consumable evidence, including `NOT_PERSISTED` transitions or `INVALID` integrity.
- Requires a non-empty validation identity.
- Preserves transition, provenance, state-key, confidence, and fingerprint identities in the validation result.
- Validation evidence is immutable and recursively freezes reasons and lineage.
- Source integrity evidence is never mutated.
- Validation is deterministic and side-effect free.

## Authority Walls

`Validation ≠ Truth`
`Validation ≠ Correctness`
`Validation ≠ Learning`
`Validation ≠ Model Update`
`Validation ≠ Authorization`
`Validation ≠ Permission`
`Validation ≠ Policy Mutation`
`Validation ≠ Execution`
`Consumption Eligibility ≠ User Intent`

M23.103 does not persist state, invoke a learner, update a model, mutate memory or policy, schedule work, create authorization, or execute actions.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation / Consumption`

M23.103 closes the explicit validation gate between transition integrity evidence and any future learning-state consumer.

## Verification Plan
Focused tests cover:
- accepted `VALID` + `PERSISTED` evidence;
- rejection of valid but non-persisted evidence;
- rejection of invalid integrity;
- exact source type gating;
- validation identity gating;
- provenance/fingerprint preservation;
- recursive immutability;
- source preservation;
- deterministic validation;
- authority and side-effect walls.

Expected focused verification: **10/10**.
Expected core regression after M23.102: **1564/1564**, with M23.103 expected to produce **1574/1574**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.102.
