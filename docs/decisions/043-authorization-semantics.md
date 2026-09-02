# Decision 043 — Authorization Semantics

## Status

M7.9 — Authorization Semantics

## Decision

Authorization is a separate deterministic system decision after policy evaluation and, when required, explicit confirmation with intact provenance.

```text
PolicyDecision
    ↓
[ConfirmationResult + ConfirmationIntegrity] when required
    ↓
AuthorizationEvaluator
    ↓
AuthorizationDecision
    ↓
Execution boundary
```

## Rules

1. `DENY` policy outcomes cannot become authorized.
2. `ALLOW` policy outcomes may become authorized without a confirmation artifact.
3. `REQUIRE_CONFIRMATION` policy outcomes require both an explicit `CONFIRMED` result and `VALID` confirmation integrity.
4. Authorization independently verifies that supplied confirmation artifacts preserve the current request, proposal identity, validation identity, and policy-decision identity.
5. A confirmation artifact from a different policy decision cannot authorize the current decision.
6. `DENIED` confirmation cannot authorize an action.
7. Confirmation and authorization identities are distinct.
8. Authorization does not select tools, invoke providers, execute actions, or mutate state.
9. Authorization metadata cannot contain execution, provider, or confirmation controls.
10. Authorization is not execution; downstream execution must consume an explicit authorization artifact at its own boundary.

## Identity chain

```text
proposal_id
    ↓
validation_id
    ↓
policy_decision_id
    ↓
confirmation_id       (only when confirmation is required)
    ↓
authorization_id
```

## Non-goals

M7.9 does not execute actions, select tools, invoke providers, mutate state, or create executable payloads.
