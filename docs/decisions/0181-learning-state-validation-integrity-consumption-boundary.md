# Decision 181 — Learning-State Validation-Integrity Consumption Boundary

Status: IMPLEMENTED / VERIFIED LOCALLY

## Purpose

M23.169 establishes a bounded downstream consumption boundary for exactly one canonical `LearningStateExecutionLearningStateValidationIntegrity` artifact.

## Contract

The service accepts exactly one canonical learning-state validation-integrity artifact and explicit consumer metadata. It consumes the artifact only when its source status is `VALID` and its integrity fingerprint fields are valid, matching SHA-256 values. The service rechecks the anchored validation-integrity lineage before producing immutable consumption evidence.

The resulting artifact preserves the source integrity identity and validation-state provenance needed to inspect the consumed evidence. A distinct consumption identity is required.

Invalid, tampered, malformed, or lineage-inconsistent integrity evidence fails closed as `REJECTED` and does not expose consumed metadata.

All caller-supplied rationale, metadata, and lineage are recursively frozen. Source integrity evidence is never mutated.

## Boundary walls

```text
Validation-Integrity Consumption ≠ Authorization
Validation-Integrity Consumption ≠ Execution
Validation-Integrity Consumption ≠ Learning
Validation-Integrity Consumption ≠ Persistence
Validation-Integrity Consumption ≠ Truth
Validation-Integrity Consumption ≠ Correctness
Validation-Integrity Consumption ≠ Certainty
```

A `CONSUMED` result means only that the integrity artifact satisfied this bounded consumption contract. It does not mean the underlying state is true, correct, certain, useful, authorized, persisted, executed, or learned.

## Verification

Focused test:

```text
python -m unittest src.core.tests.test_learning_state_execution_learning_state_validation_integrity_consumption -v
```

The focused suite covers canonical type enforcement, explicit/distinct identity, required metadata, invalid-source rejection, anchored lineage checks, malformed/mismatched fingerprints, immutable output, provenance preservation, source non-mutation, and authority-boundary walls.
