# M23.74 — Adaptation Decision v3

## Purpose
M23.74 establishes the decision boundary immediately after M23.73 adaptation proposal v3.

The service converts one immutable adaptation-proposal artifact into inert decision evidence. A proposed adaptation may be accepted or rejected; a blocked proposal remains blocked. The decision never authorizes, schedules, executes, or persists adaptation.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3` artifact.
- `PROPOSED` + `accept=True` → `ACCEPTED`.
- `PROPOSED` + `accept=False` → `REJECTED`.
- `BLOCKED` → `BLOCKED` regardless of requested acceptance.
- Preserves proposal provenance, v3 lineage, confidence, fingerprints, authority/executor evidence, failure evidence, and source identities.
- New `decision_id` identifies the decision; upstream proposal IDs remain source evidence.
- Recursively freezes decision basis, reasons, and lineage.
- Wrong source type or blank decision ID fails closed.

## Authority walls
Decision ≠ Authorization.
Decision ≠ Permission.
Decision ≠ Execution.
Decision ≠ Adaptation.
Decision ≠ Model Update.
Decision ≠ Memory Mutation.
Decision ≠ Policy Mutation.
Decision ≠ Persistence Mutation.
Decision ≠ Scheduling.
Decision ≠ Authority.
Decision ≠ Truth.
Decision ≠ User Intent.

An `ACCEPTED` decision records a bounded determination about an adaptation candidate. It does not grant the capability or authorization required to enact that adaptation.

## Immutability
The decision artifact is frozen and recursively freezes decision basis, reasons, and lineage. The source proposal remains unchanged.

## Verification target
Focused tests should cover:
- proposed evidence becoming accepted;
- proposed evidence becoming rejected;
- blocked evidence remaining blocked;
- blocked proposals overriding an attempted acceptance;
- provenance and fingerprint preservation;
- recursive immutability;
- advisory authority walls;
- wrong source type rejection;
- blank decision ID rejection;
- decision-status mapping enforcement;
- source preservation.

No adaptation, authorization, execution, scheduling, model update, memory mutation, policy mutation, or persistence mutation is introduced.

## Atomicity target
Parent: `50a6aadfe11e0005e475723a060857b0bed4cf6e` — user-verified M23.73 point with focused 10/10 and core regression 1223/1223.

Exactly three intended files:
- `src/core/environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3.py`
- `src/core/tests/test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3.py`
- `docs/decisions/072-adaptation-decision-v3.md`

No merge unless explicitly requested.
