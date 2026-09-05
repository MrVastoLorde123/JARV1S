# Decision 013 — Explicit Authorization Boundary

**Status:** Accepted

## Context

M22.7 establishes a structurally validated `ToolRequest`, but structural
validity is not authority. The existing tool stack already separates policy
from confirmation, yet the authorization transition remained implicit inside
`PolicyGate.invoke()`.

JARVIS needs an inspectable authority artifact so downstream execution can
consume an explicit authorization result rather than inferring authority from
a successful validation, policy verdict, or confirmation response.

## Decision

Introduce `AuthorizationDecision` and `ExplicitAuthorizationService` as the
non-executing authorization boundary. `PolicyGate.authorize()` exposes this
boundary; `PolicyGate.invoke()` consumes the resulting decision before calling
`ToolService`.

```text
Validated ToolRequest
        ↓
Policy
        ↓
Confirmation (when required)
        ↓
Explicit AuthorizationDecision
        ↓
ToolService
```

Authorization is granted only when policy permits the request and, when
confirmation is required, the confirmation provider explicitly approves it.
A policy denial or confirmation denial produces a denied authorization result.

## Authority walls

- `Validated ToolRequest ≠ Authorized ToolRequest`
- `Policy ALLOW ≠ Implicit Execution`
- `Confirmation ≠ Execution`
- `Authorization ≠ Execution`
- `Permission ≠ Authorization`
- `Sandbox ≠ Authorization`

## Constraints

- `ExplicitAuthorizationService` never invokes tools.
- `PolicyGate.authorize()` never invokes `ToolService`.
- `PolicyGate.invoke()` remains the only path in the gate that reaches
  `ToolService`.
- Authorization must not be inferred from capability selection, argument
  generation, lifecycle, trust, permission binding, or sandbox admission.
- Authorization decisions are immutable and inspectable.
- Malformed policy verdicts and confirmation responses remain structural
  errors rather than becoming authorization.

## Identity

The authorization artifact carries an explicit `authorization_id` and the
request's `invocation_id`, allowing downstream execution to maintain the
existing lineage:

`proposal_id → validation_id → policy_decision_id → confirmation_id → authorization_id → execution_id`

The initial gate can derive a deterministic authorization identifier when a
caller does not provide one; this identifier is correlation metadata, not a
permission source.

## Consequences

Positive:

- Authorization becomes a first-class, reviewable boundary.
- Execution cannot be inferred merely because request construction succeeded.
- Existing policy and confirmation implementations remain replaceable.
- The existing `PolicyGate` continues to protect `ToolService`.

Deliberate exclusion:

- No sandbox execution is added here.
- No plugin worker is selected here.
- No authorization persistence/revocation lifecycle is added here.
