# M23.81 — Adaptation Application Learning Signal Integrity v3

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`ba3e8ae35f9c877f7db57a5918e38b2b8b717e40` — M23.80 locally verified: focused `14/14`, core `1305/1305`.

## Purpose
Establish the integrity boundary immediately after M23.80 adaptation-application learning signal v3.

M23.81 verifies one concrete v3 application learning signal and emits immutable advisory integrity evidence with a deterministic SHA-256 fingerprint. Integrity is evidence about representation, not truth or authority.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3` artifact.
- Produces `VALID` integrity evidence with a deterministic SHA-256 fingerprint over the complete M23.80 learning-signal representation.
- Covers positive, negative, and rejection application learning signals.
- Preserves complete v3 application provenance, provenance identities, state, fingerprints, confidence, feedback-signal identity, authority/executor evidence where valid, failure/rejection evidence, reasons, and lineage.
- Does not invent or require `execution_status`; M23.80 does not expose that field.
- Recursively freezes reasons and lineage; source learning signal remains unchanged.
- Invalid source type or blank integrity ID fails closed.

## Rejection boundary
`REJECTION_SIGNAL` carries no failure evidence, authority, or executor evidence. Its integrity record preserves the bounded upstream representation rather than creating action authority.

## Authority walls
Integrity ≠ Truth.
Integrity ≠ Learning.
Integrity ≠ Adaptation.
Integrity ≠ Retry Permission.
Integrity ≠ Authorization.
Integrity ≠ Scheduling.
Integrity ≠ Execution.
Integrity ≠ Model Update.
Integrity ≠ Memory Mutation.
Integrity ≠ Policy Mutation.
Integrity ≠ Persistence Mutation.
Integrity ≠ User Intent.

M23.81 is advisory-only. It does not update models, memory, policy, persistence, schedules, authority, retry permission, or execution state.

## Fingerprint scope
The canonical fingerprint covers all M23.80 source fields, including:

`signal_id`, `evaluation_id`, `feedback_id`, `classification_id`, `integrity_id`, `application_id`, `decision_id`, `proposal_id`, `source_proposal_id`, `eligibility_id`, `source_integrity_id`, `feedback_signal_id`, `feedback_source_id`, `source_evaluation_id`, `execution_id`, `handoff_id`, `authorization_id`, `validation_id`, `source_signal_id`, `outcome_id`, `preparation_id`, `assessment_id`, `environment_id`, `expected_model_id`, `observed_model_id`, `proposal_kind`, `proposal_status`, `decision_status`, `application_status`, `integrity_status`, `outcome_status`, `feedback_status`, `evaluation_status`, `signal_status`, `confidence`, `signal_fingerprint`, `upstream_proposal_fingerprint`, `handoff_fingerprint`, `result_fingerprint`, `application_fingerprint`, `authority_principal_id`, `executor_id`, `failure_reason`, `reasons`, and `lineage`.

Canonicalization is deterministic and uses SHA-256 over the canonical UTF-8 JSON representation.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.80.

## Local verification
Pending user local receipt.

Expected focused: **10/10**.
Expected core regression: **1315/1315**.

No merge unless explicitly requested.
