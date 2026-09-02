# Decision 040 — Validation Identity Separation

## Status

M7.7.1 — Validation Identity Repair

## Decision

A consequence proposal and the validation result produced for that proposal are
distinct semantic artifacts and MUST have distinct identities.

```text
proposal_id
    ↓
validation_id
    ↓
policy_decision_id
    ↓
confirmation_id
    ↓
execution_id
```

`proposal_id` identifies the proposed consequence. `validation_id` identifies
the specific validation result that established whether that proposal crossed
the consequence-validation boundary.

## Rules

1. `ConsequenceValidation` carries both `proposal_id` and `validation_id`.
2. A validation result MUST preserve its own non-empty `validation_id`.
3. `ConsequenceValidationEngine.validate()` accepts an optional explicit
   `validation_id`; when omitted it derives a deterministic identity as
   `validation:<proposal_id>` for compatibility with single-proposal calls.
4. `validate_all()` assigns deterministic collection identities
   `validation:0`, `validation:1`, and so on, independently of proposal IDs.
5. `PolicyInputProjector` MUST propagate `validation.validation_id` rather than
   reusing `validation.proposal_id`.
6. Policy provenance MUST preserve both proposal and validation identity.
7. Identity separation does not grant authority, confirmation, or execution.

## Rationale

A proposal may be evaluated more than once. Reusing the proposal identity for
the validation result collapses two different semantic stages and makes later
policy, confirmation, and execution provenance ambiguous.

Keeping validation identity distinct allows downstream decisions to refer to
the exact validation result they consumed.

## Non-goals

This decision does not introduce timestamps, globally unique identifiers,
cryptographic attestations, confirmation semantics, or execution tracking.
Those concerns belong to later lifecycle boundaries.
