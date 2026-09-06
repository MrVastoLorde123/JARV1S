# M23.71 — Adaptation Execution Learning Signal Integrity v3

## Purpose
M23.71 establishes the integrity boundary immediately after M23.70 adaptation-execution learning signal v3.

The service verifies one immutable v3 learning signal and emits immutable advisory integrity evidence with a deterministic SHA-256 fingerprint. Integrity evidence does not itself constitute learning, adaptation, authorization, retry permission, scheduling, execution, persistence, policy mutation, memory mutation, or user intent.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3` artifact.
- Produces `VALID` integrity evidence for the supplied concrete learning signal.
- Fingerprints the complete v3 learning-signal representation, including provenance, signal state, confidence, fingerprints, authority/executor evidence, failure/rejection evidence, reasons, and lineage.
- Preserves the complete v3 provenance chain and source identifiers.
- Recursively freezes reasons and lineage.
- Source learning signal remains unchanged.
- Invalid source type or blank integrity ID fails closed.

## Integrity boundary
Integrity ≠ Truth.
Integrity ≠ Learning.
Integrity ≠ Adaptation.
Integrity ≠ Retry Permission.
Integrity ≠ Authorization.
Integrity ≠ Scheduling.
Integrity ≠ Execution.
Integrity ≠ Policy Mutation.
Integrity ≠ Memory Mutation.
Integrity ≠ Persistence Mutation.
Integrity ≠ User Intent.

The M23.71 service is advisory-only. It computes evidence about representation integrity and does not change the learning signal, model, memory, policy, persistence, authority, schedule, or execution state.

## Immutability
The integrity artifact is frozen at the outer dataclass and recursively freezes reasons and lineage. The source signal is never mutated.

## Verification target
Focused tests cover:
- valid positive learning signal integrity;
- valid negative learning signal integrity;
- valid rejection learning signal integrity;
- deterministic fingerprinting;
- blank integrity ID rejection;
- wrong source type rejection;
- provenance preservation;
- recursive immutability;
- source preservation;
- advisory-only authority, learning, retry, scheduling, execution, and mutation walls.

No model update, learning application, adaptation, retry authorization, execution, scheduling, persistence, policy mutation, or memory mutation is introduced.