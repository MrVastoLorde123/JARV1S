# Decision 117 — Learning-State Consumption Read Boundary

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`c01afd6a48553fd6effbb00d1931cdaf9cff95e4` — M23.104 Learning-State Consumption Request Boundary.

## Purpose
M23.105 establishes the first actual caller-owned consumer boundary after the M23.104 consumption request. A `READY` consumption request may be handed to an injected read-only storage adapter, which returns one bounded learning-state payload as immutable consumption evidence.

The consumer performs at most one caller-supplied read attempt. It does not write storage, retry, invoke learning, update a model, mutate memory or policy, create authority, schedule work, or execute actions.

## Contract
- Consumes exactly one canonical `LearningStateConsumptionRequest` artifact.
- Requires request status `READY`.
- Requires an injected callable read adapter for durable-state access.
- Passes only bounded request identity metadata and `state_key` to the adapter.
- Adapter exceptions, non-mapping results, or a missing adapter produce `REJECTED` consumption evidence without retry.
- A successful mapping result is recursively frozen and emitted as immutable consumption evidence.
- Preserves request, validation, integrity, transition, evidence, application, state-key, and fingerprint identities.
- Source request is never mutated.
- The read adapter is invoked at most once per consumption call.

## Authority Walls
`Consumption ≠ Write`
`Consumption ≠ Learning`
`Consumption ≠ Truth`
`Consumption ≠ Correctness`
`Consumption ≠ Authorization`
`Consumption ≠ Permission`
`Consumption ≠ Policy Mutation`
`Consumption ≠ Execution`
`Read Success ≠ Truth`
`Read Success ≠ Correctness`

M23.105 does not write durable state, retry reads, invoke a learner, update a model, mutate memory or policy, schedule work, create authorization, or execute actions.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption`

M23.105 closes the first caller-owned read boundary after the consumption request while preserving separation from all mutation and authority-bearing paths.

## Verification Plan
Focused tests cover READY-source gating, rejected-source handling, wrong-source rejection, read-adapter invocation, bounded adapter input, successful mapping consumption, recursive immutability, provenance preservation, source preservation, adapter exception handling, malformed adapter output, single-attempt behavior, determinism, and authority/side-effect walls.

Expected focused verification: **13/13**.
Expected core regression after M23.104: **1597/1597**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.104.
