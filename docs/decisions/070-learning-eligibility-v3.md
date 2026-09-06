# M23.72 — Learning Eligibility v3

## Purpose
M23.72 establishes the eligibility boundary immediately after M23.71 learning-signal integrity v3.

The service assesses whether one learning-signal integrity artifact is structurally eligible to proceed to a later learning boundary. Eligibility is evidence, not learning, adaptation, permission, authority, or execution.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3` artifact.
- `VALID` integrity → `ELIGIBLE` learning-eligibility evidence.
- `INVALID` integrity → `INELIGIBLE` learning-eligibility evidence.
- Preserves the complete v3 provenance, signal/evaluation lineage, confidence, fingerprints, authority/executor evidence, failure evidence, and source identities.
- Recursively freezes reasons and lineage; source integrity evidence remains unchanged.
- Wrong source type or blank eligibility ID fails closed.

## Authority walls
Eligibility ≠ Learning.
Eligibility ≠ Adaptation.
Eligibility ≠ Permission.
Eligibility ≠ Authorization.
Eligibility ≠ Authority.
Eligibility ≠ Retry Permission.
Eligibility ≠ Scheduling.
Eligibility ≠ Execution.
Eligibility ≠ Policy Mutation.
Eligibility ≠ Memory Mutation.
Eligibility ≠ Persistence Mutation.
Eligibility ≠ Truth.

An `ELIGIBLE` artifact is evidence that the preceding integrity boundary is valid enough for a later learning boundary to consider. It does not authorize or perform learning.

## Immutability
The eligibility artifact is frozen at the outer dataclass and recursively freezes reasons and lineage. The source integrity artifact remains unchanged.

## Verification target
Focused tests cover:
- valid integrity becoming eligible;
- invalid integrity becoming ineligible;
- blank eligibility ID rejection;
- wrong source type rejection;
- provenance and fingerprint preservation;
- recursive immutability;
- source preservation;
- status mapping enforcement;
- advisory-only learning, authority, mutation, scheduling, and execution walls.

No model update, memory mutation, policy mutation, persistence mutation, retry, scheduling, authorization, or execution is introduced.

## Atomicity target
Parent: `2ec56a8763ba064a7a2f7b80c26e029a04edfed7` (M23.71 verified HEAD).

Exactly three intended files:
- `src/core/environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3.py`
- `src/core/tests/test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3.py`
- `docs/decisions/070-learning-eligibility-v3.md`

No merge unless explicitly requested.