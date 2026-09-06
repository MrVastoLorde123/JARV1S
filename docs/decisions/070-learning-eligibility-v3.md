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
M23.72 implementation delta from its corrected M23.71 prerequisite:

- Parent: `33ea4ec3b1fe7847ef1f54d76f3f16846cfc1477`
- Exactly 1 M23.72 commit / 3 intended files.

The prerequisite M23.71 fixture repair is isolated in commit `33ea4ec3b1fe7847ef1f54d76f3f16846cfc1477`.

No merge unless explicitly requested.
