# Decision 110 — Learning-State Transition V4

## Status
VERIFIED / COMPLETE

## Parent
`2cbc44c8e9f9858243a0b856cceb5b30767f2bd4` — M23.97 Learning-State Evidence V4.

## Purpose
M23.98 establishes the explicit transition boundary from immutable learning-state evidence into a caller-owned durable learning-state store.

The boundary accepts exactly one M23.97 `READY` evidence artifact, validates the supplied transition metadata, invokes one injected persistence adapter, and returns immutable transition evidence describing whether persistence succeeded. Persistence is opt-in and occurs only through the injected adapter supplied by the caller.

## Contract
- Consumes exactly one M23.97 learning-state evidence v4 artifact.
- Requires evidence status `READY`.
- Requires a non-empty transition identity and non-empty state key.
- Requires a mapping state payload and recursively freezes it.
- Preserves complete upstream evidence/provenance and application fingerprints.
- The raw upstream evidence payload is never passed to the persistence adapter.
- Invokes at most one injected persistence adapter when supplied.
- Adapter receives only bounded transition metadata: `transition_id`, `evidence_id`, `application_id`, and `state_key`, plus the bounded state payload.
- Adapter success is represented by boolean `True`; `False`, malformed results, exceptions, and absent adapters produce `NOT_PERSISTED` without retry.
- Source evidence is never mutated.
- Transition evidence and nested state/reasons/lineage are recursively immutable.

## Authority walls
A persisted learning state is a durable record, not authorization or truth.

`Learning-State Transition ≠ Authorization`
`Learning-State Transition ≠ Truth`
`Learning-State Transition ≠ Model Update`
`Learning-State Transition ≠ Policy Mutation`
`Learning-State Transition ≠ Execution`
`Persistence ≠ Permission`
`Storage Success ≠ Correctness`

M23.98 does not invoke a learner, update a model, mutate policy, schedule work, execute actions, create authorization, infer user intent, or treat persisted state as factual truth.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Durable Learning State`

The persistence adapter is an explicit dependency and is the only component permitted by this boundary to perform durable storage.

## Verification
Focused verification: **16/16**.
Core regression: **1544/1544**.

The focused suite contains sixteen tests covering READY-only gating, persistence success/failure semantics, bounded adapter input, provenance/fingerprint preservation, identity/state-key validation, state mapping validation, recursive immutability, source preservation, authority walls, and absence of implicit learner/policy/authorization objects.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.97.
