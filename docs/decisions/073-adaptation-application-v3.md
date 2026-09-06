# M23.75 — Adaptation Application v3

## Purpose
M23.75 establishes the bounded application boundary after M23.74 adaptation decision v3.

The boundary consumes one matching M23.74 decision and M23.73 proposal. Only an `ACCEPTED` decision may reach the replaceable internal adaptation applier. `REJECTED` becomes `NOT_APPLIED`; `BLOCKED` becomes `BLOCKED`. An applier failure becomes `NOT_APPLIED` failure evidence.

## Contract
- Consumes exactly one M23.74 adaptation-decision v3 artifact and its matching M23.73 adaptation-proposal v3 source artifact.
- Requires decision/proposal proposal identity, source-proposal identity, proposal status, and environment identity to match.
- `ACCEPTED` requires a proposal payload and a replaceable applier.
- Successful applier output must be a mapping and yields `APPLIED` application evidence.
- Applier exceptions are normalized into `NOT_APPLIED` with failure evidence.
- `REJECTED` never invokes the applier and yields `NOT_APPLIED`.
- `BLOCKED` never invokes the applier and yields `BLOCKED`.
- Preserves complete known v3 provenance, confidence, fingerprints, authority/executor evidence, and source identities.
- Recursively freezes applied payload, application result, reasons, and lineage.
- Source decision and proposal artifacts remain unchanged.

## Authority walls
Application ≠ Authorization.
Application ≠ Permission.
Application ≠ External Capability Execution.
Application ≠ New Authority.
Application ≠ Truth.
Application ≠ User Intent.
Application ≠ Scheduling.
Application ≠ Policy Mutation.
Application ≠ Persistence Coordination.

This boundary mutates only the explicitly injected internal adaptation target through the replaceable applier. It does not invoke JARVIS capabilities/plugins, bypass validation/policy/confirmation/authorization, or grant external execution authority.

## Failure semantics
```text
ACCEPTED + successful applier → APPLIED
ACCEPTED + applier failure    → NOT_APPLIED + failure evidence
REJECTED                      → NOT_APPLIED
BLOCKED                       → BLOCKED
```

## Immutability
The application artifact is frozen. Applied payload, application result, reasons, and lineage are recursively immutable. Upstream decision and proposal artifacts are never mutated.

## Verification target
Focused tests should cover:
- accepted application invoking the applier;
- rejected decision not invoking the applier;
- blocked decision not invoking the applier;
- accepted application requiring an applier;
- applier exception normalization;
- wrong source types;
- decision/proposal identity mismatch;
- recursive immutability;
- provenance/fingerprint preservation;
- explicit authority walls;
- invalid `APPLIED` constructor shape.

## Atomicity target
Parent: `600820c29857cab0315ce4639148f4d65003db47` — user-verified M23.74 focused 11/11 and core 1234/1234.

Exactly three intended files:
- `src/core/environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3.py`
- `src/core/tests/test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3.py`
- `docs/decisions/073-adaptation-application-v3.md`

No merge unless explicitly requested.
