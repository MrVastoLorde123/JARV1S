# M23.73 — Adaptation Proposal v3

## Purpose
M23.73 establishes the adaptation-proposal boundary immediately after M23.72 learning eligibility v3.

The service converts one immutable learning-eligibility artifact into inert proposal evidence. A proposal may describe an adaptation candidate, but it never authorizes, schedules, executes, or persists adaptation.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3` artifact.
- `ELIGIBLE` → `PROPOSED` with kind `ADAPTATION_CANDIDATE` and a required mapping payload.
- `INELIGIBLE` → `BLOCKED` with kind `BLOCKED_ADAPTATION_CANDIDATE` and no payload.
- Preserves v3 provenance, lineage, confidence, fingerprints, authority/executor evidence, failure evidence, and source identities.
- The new `proposal_id` identifies this proposal; `source_proposal_id` preserves the upstream M23.72 eligibility `proposal_id`.
- Recursively freezes proposal payload, reasons, and lineage.
- Wrong source type or blank proposal ID fails closed.

## Authority walls
Proposal ≠ Adaptation.
Proposal ≠ Permission.
Proposal ≠ Authorization.
Proposal ≠ Execution.
Proposal ≠ Model Update.
Proposal ≠ Memory Mutation.
Proposal ≠ Policy Mutation.
Proposal ≠ Persistence Mutation.
Proposal ≠ Scheduling.
Proposal ≠ Authority.
Proposal ≠ Truth.
Proposal ≠ User Intent.

An `ADAPTATION_CANDIDATE` is descriptive evidence for a later decision boundary. It is not executable intent.

## Immutability
The proposal artifact is frozen and recursively freezes payload, reasons, and lineage. The source eligibility artifact remains unchanged. Blocked proposals cannot retain a candidate payload.

## Verification target
Focused tests cover:
- eligible evidence becoming proposed;
- ineligible evidence becoming blocked;
- payload requirements and discard-on-blocking;
- provenance and fingerprint preservation;
- recursive immutability;
- advisory authority walls;
- wrong source type rejection;
- blank proposal ID rejection;
- constructor status mapping enforcement;
- source preservation.

No adaptation, authorization, execution, scheduling, model update, memory mutation, policy mutation, or persistence mutation is introduced.

## Atomicity target
Parent: `1f209f8457b5e61e8c8d749a804205cae167ab3f` — user-verified M23.72 point with focused 9/9 and core regression 1213/1213.

Exactly three intended files:
- `src/core/environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3.py`
- `src/core/tests/test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3.py`
- `docs/decisions/071-adaptation-proposal-v3.md`

No merge unless explicitly requested.
