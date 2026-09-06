# Decision 103 â€” Application Learning Signal Integrity V4

## Status
IMPLEMENTED / VERIFIED / COMPLETE

## Purpose
M23.91 establishes an explicit integrity boundary over the M23.90 application learning signal v4 artifact.

The boundary exists to prove that one exact v4 learning-signal representation can be structurally validated and deterministically fingerprinted without converting integrity evidence into truth, learning authority, retry permission, execution permission, scheduling permission, model update authority, memory mutation, policy mutation, or persistence mutation.

## Contract
M23.91 accepts exactly one M23.90 application learning signal v4 artifact and emits one immutable integrity-evidence artifact.

The integrity evidence must preserve the complete M23.90 provenance relevant to the learning signal, including:

- signal identity
- evaluation, feedback, feedback-source, classification, integrity, application, decision, proposal, and outcome identities
- outcome and feedback status
- confidence
- upstream signal, result, and application fingerprints
- failure evidence
- evaluation and learning-signal status
- reasons and lineage

The integrity boundary computes a deterministic SHA-256 fingerprint over the complete source representation, including recursively represented reasons and lineage. Canonicalization must make mapping key order irrelevant while preserving list/tuple order and deterministically ordering sets.

## Rejection Boundary
The service fails closed when:

- the supplied source is not the exact M23.90 learning-signal v4 type
- the integrity identifier is blank or malformed
- a supposedly valid integrity artifact does not carry SHA-256 fingerprints
- required immutable evidence fields violate their declared contract

No best-effort coercion of a different signal generation into v4 is permitted.

## Atomicity and Immutability
The source learning signal is observationally consumed and must remain unchanged.

The emitted integrity evidence is a frozen dataclass. Reasons and lineage are recursively frozen so downstream callers cannot mutate integrity evidence through nested structures.

## Authority Walls
Integrity is evidence, not authority.

The M23.91 artifact is:

- advisory-only
- observational
- non-authoritative
- not retry authorization
- not retry request
- not execution
- not scheduling
- not a model update
- not memory mutation
- not policy mutation
- not persistence mutation
- not user intent
- not truth

The architecture remains:

`Outcome â†’ Feedback â†’ Evaluation â†’ Learning Signal â†’ Learning Signal Integrity â†’ (future learning/update boundary)`

M23.91 does not cross the downstream learning/update boundary.

## Verification Plan
Focused test target:

`src.core.tests.test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_learning_signal_integrity_v4`

Verified focused verification: **12/12**.

Core regression verification: **1441/1441** after M23.91.

No merge is implied by this decision. M23.91 local verification is complete.

