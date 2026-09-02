# Decision 041 — Confirmation Semantics

## Status

M7.8 — Confirmation Semantics

## Decision

Confirmation is an explicit human authorization boundary between policy evaluation and execution. A policy decision may require confirmation, but it never performs or records that confirmation itself.

```text
PolicyDecision
    ↓
ConfirmationRequest
    ↓
human decision
    ↓
ConfirmationResult
    ↓
Execution boundary
```

## Identity

Confirmation preserves the complete upstream identity chain:

```text
proposal_id
    ↓
validation_id
    ↓
policy_decision_id
    ↓
confirmation_id
```

Each artifact has its own semantic identity. Confirmation must never reuse proposal, validation, or policy-decision identity as its own identifier.

## Rules

1. Only `REQUIRE_CONFIRMATION` policy decisions may create a confirmation request.
2. `ALLOW` does not create a confirmation request and remains distinct from confirmation.
3. `DENY` is a hard stop and cannot enter confirmation.
4. A confirmation request preserves request, proposal identity, validation identity, and policy-decision identity.
5. A confirmation resolution must be either `CONFIRMED` or `DENIED`; `PENDING` is not a resolution.
6. `CONFIRMED` means the explicit confirmation boundary has been satisfied for that confirmation artifact; it does not itself invoke tools or execute an action.
7. `DENIED` means confirmation was not granted and therefore cannot authorize downstream execution.
8. Confirmation artifacts contain no execution controls, tool handles, or implicit authorization fields beyond the explicit confirmation state.
9. Confirmation semantics are deterministic and provider-neutral.
10. Confirmation does not mutate policy inputs, policy decisions, proposals, or reasoning context.

## Non-goals

M7.8 does not execute actions, select tools, invoke providers, mutate external state, or implement the execution boundary.
