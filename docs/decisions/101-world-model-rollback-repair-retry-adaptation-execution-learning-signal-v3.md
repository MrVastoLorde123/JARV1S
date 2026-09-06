# M23.70 — Adaptation Execution Learning Signal v3

## Purpose
M23.70 establishes the learning-signal boundary after M23.69 adaptation-execution feedback evaluation.

M23.69 produces observational evaluation evidence. M23.70 converts that evidence into an immutable learning signal without performing learning, adaptation, authorization, retry, scheduling, or mutation.

## Contract
- `SUCCESS_EVALUATION` → `POSITIVE_SIGNAL`
- `FAILURE_EVALUATION` → `NEGATIVE_SIGNAL`
- `REJECTION_EVALUATION` → `REJECTION_SIGNAL`
- Preserve complete v3 provenance, confidence, signal/proposal/handoff/result fingerprints, execution identity, authority/executor evidence where valid, failure/rejection evidence, reasons, and lineage.
- Recursively freeze reasons and lineage; source evaluation remains unchanged.
- Fail closed on wrong source type, blank signal ID, invalid confidence, status mismatch, malformed rejection authority/executor evidence, or inconsistent result/failure evidence.

## Authority walls
Learning Signal != Learning.
Learning Signal != Adaptation.
Learning Signal != Retry Permission.
Learning Signal != Authorization.
Learning Signal != Scheduling.
Learning Signal != Execution.
Learning Signal != Policy Mutation.
Learning Signal != Memory Mutation.
Learning Signal != Persistence Mutation.
Learning Signal != New Authority.
Learning Signal != User Intent.

The M23.70 service is advisory-only. It emits evidence for a later learning stage but does not update a model, memory, policy, persistence layer, schedule, or authority state.

## Immutability
The produced learning signal is frozen at the outer dataclass and recursively freezes reasons and lineage. The source evaluation remains unchanged.

## Verification target
Focused tests cover:
- success evaluation becoming positive learning signal;
- failure evaluation becoming negative learning signal;
- rejection evaluation becoming rejection learning signal;
- blank signal ID rejection;
- wrong source type rejection;
- confidence bounds;
- status mismatch rejection;
- preservation of provenance and fingerprints;
- recursive immutability;
- source preservation;
- rejection authority/executor wall;
- learning/adaptation/retry/authority/scheduling/mutation walls.
