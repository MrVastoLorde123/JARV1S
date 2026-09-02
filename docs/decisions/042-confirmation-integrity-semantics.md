# Decision 042 — Confirmation Integrity Semantics

## Status

M7.8.1 — Confirmation Integrity

## Decision

Confirmation integrity is a deterministic boundary that verifies that a `ConfirmationResult` remains bound to the exact `ConfirmationRequest` and upstream `PolicyDecision` that produced it.

```text
PolicyDecision
      ↓
ConfirmationRequest
      ↓
ConfirmationResult
      ↓
ConfirmationIntegrityValidator
      ↓
ConfirmationIntegrity
```

## Integrity requirements

1. The confirmation request must be derived from a `REQUIRE_CONFIRMATION` policy decision.
2. Request and result must preserve the exact request identity.
3. Request and result must preserve the exact `proposal_id`.
4. Request and result must preserve the exact `validation_id`.
5. Request and result must preserve the exact `policy_decision_id`.
6. The result must resolve the exact `confirmation_id` issued by the request.
7. A `PENDING` result is not a terminal integrity-valid resolution.
8. Any provenance mismatch produces an `INVALID` integrity result.
9. `VALID` integrity means provenance continuity only; it is not authorization, approval, confirmation, or execution authority.
10. Integrity validation never mutates state, selects tools, invokes providers, or executes actions.

## Non-goals

M7.8.1 does not grant authorization, create execution payloads, select tools, or consume external credentials.
