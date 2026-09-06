# M23.76 — Adaptation Application Integrity v3

## Purpose
M23.76 establishes the immutable integrity boundary immediately after M23.75 adaptation application v3.

The boundary verifies one bounded adaptation-application artifact as representation evidence. It does not re-apply the adaptation, authorize anything, execute capabilities, or decide whether the adaptation was desirable.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3` artifact.
- `APPLIED` requires an `ACCEPTED` decision, an applied payload, an application result, and no failure evidence.
- `NOT_APPLIED` is valid for a rejected decision with no action evidence, or an accepted decision with normalized failure evidence.
- `BLOCKED` requires a `BLOCKED` decision and carries no action evidence or failure evidence.
- Produces `VALID` or `INVALID` immutable integrity evidence.
- Produces a deterministic SHA-256 `application_fingerprint` over the application representation.
- Preserves complete known v3 provenance, confidence, fingerprints, authority/executor evidence, and source identities.
- Recursively freezes applied payload, application result, reasons, and lineage.
- Source application artifact remains unchanged.
- Invalid application structure is represented as `INVALID` evidence with failure reasoning; wrong source type and blank integrity ID fail closed.

## Integrity semantics
```text
APPLIED + ACCEPTED + payload + result + no failure → VALID
NOT_APPLIED + REJECTED + no payload/result       → VALID
NOT_APPLIED + ACCEPTED + failure evidence        → VALID
BLOCKED + BLOCKED + no action evidence           → VALID
Any inconsistent representation                  → INVALID
```

The fingerprint identifies the observed application representation. Integrity remains evidence about representation, not proof that the underlying adaptation was correct, beneficial, safe in the world, or authorized beyond the already-existing boundaries.

## Authority walls
Application Integrity ≠ Truth.
Application Integrity ≠ Learning.
Application Integrity ≠ Adaptation Authorization.
Application Integrity ≠ Permission.
Application Integrity ≠ Retry Authorization.
Application Integrity ≠ Scheduling.
Application Integrity ≠ Execution.
Application Integrity ≠ Model Update.
Application Integrity ≠ Memory Mutation.
Application Integrity ≠ Policy Mutation.
Application Integrity ≠ Persistence Mutation.
Application Integrity ≠ User Intent.

The M23.76 service is advisory-only. It does not modify the application, adaptation target, model, memory, policy, persistence, authority, schedule, or external capabilities.

## Verification target
Focused tests should cover:
- applied/accepted application becoming valid;
- rejected/not-applied application becoming valid;
- accepted application failure becoming valid failure evidence;
- blocked application becoming valid;
- tampered application becoming invalid;
- deterministic application fingerprinting;
- recursive immutability;
- wrong source type rejection;
- blank integrity ID rejection;
- advisory authority walls;
- source application preservation.

## Atomicity target
Parent: `2cd783e4e98b172c83e1dfd9720074544c1e928f` — clean M23.75 verified point, reconstructed as exactly one commit over the user-verified M23.74 parent.

Exactly three intended files:
- `src/core/environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3.py`
- `src/core/tests/test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3.py`
- `docs/decisions/074-adaptation-application-integrity-v3.md`

No merge unless explicitly requested.
