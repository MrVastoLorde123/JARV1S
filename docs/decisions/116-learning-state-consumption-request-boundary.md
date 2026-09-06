# Decision 116 — Learning-State Consumption Request Boundary

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`d36697f399d278214fdf65c709224c7d6e9c2c52` — M23.103 Learning-State Integrity Validation Boundary.

## Purpose
M23.104 establishes the first bounded consumer handoff after learning-state integrity validation. An `ACCEPTED` M23.103 validation result may be converted into an immutable consumption request identifying the learning-state artifact that a future caller-owned consumer may read.

The request is a declaration of what may be consumed; it does not read storage, write storage, invoke learning, update a model, mutate memory or policy, create authority, schedule work, or execute actions.

## Contract
- Consumes exactly one canonical `LearningStateTransitionIntegrityValidation` artifact.
- Requires validation status `ACCEPTED`.
- Rejects `REJECTED` validation evidence and wrong source types.
- Requires a non-empty consumption-request identity.
- Preserves validation, integrity, transition, evidence, application, state-key, and fingerprint identities.
- Emits immutable request metadata with recursively frozen reasons and lineage.
- Does not contain a durable-state payload and does not perform a storage read.
- Repeated construction from equivalent accepted validation evidence is deterministic.

## Authority Walls
`Consumption Request ≠ Consumption`
`Consumption ≠ Learning`
`Consumption ≠ Truth`
`Consumption ≠ Correctness`
`Consumption ≠ Authorization`
`Consumption ≠ Permission`
`Consumption ≠ Policy Mutation`
`Consumption ≠ Execution`
`Accepted Validation ≠ User Intent`

M23.104 does not read or mutate a durable store, invoke a learner, update a model, mutate memory or policy, schedule work, create authorization, or execute actions.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → (future caller-owned learning-state consumer)`

## Verification Plan
Focused tests cover accepted-source gating, rejection of non-accepted validation, wrong-source rejection, identity gating, provenance/fingerprint preservation, deterministic request formation, recursive immutability, source preservation, absence of state payload reads, and authority/side-effect walls.

Expected focused verification: **10/10**.
Expected core regression after M23.103: **1574/1574**, with M23.104 expected to produce **1584/1584**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.103.
