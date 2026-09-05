# M22.8 — Explicit Authorization Boundary

## Purpose

M22.8 establishes the first-class authority transition between a validated
tool request and downstream execution.

```text
Validated ToolRequest
        ↓
Policy
        ↓
Confirmation (when required)
        ↓
AuthorizationDecision
        ↓
Sandbox
        ↓
Execution
```

## Contract

- `AuthorizationDecision` is immutable and inspectable.
- `ExplicitAuthorizationService` evaluates the existing policy contract and,
  when required, the existing confirmation contract.
- `PolicyGate.authorize()` exposes authorization without executing a tool.
- `PolicyGate.invoke()` consumes the authorization result and only then calls
  `ToolService`.
- Policy denial always yields denied authorization.
- Confirmation-required requests are authorized only after explicit approval.
- Authorization identity is explicit and correlatable to the request.
- Authorization remains separate from permission, sandbox admission, and
  execution.

## Authority walls

```text
Validated ToolRequest ≠ Authorized ToolRequest
Policy ALLOW ≠ Implicit Execution
Confirmation ≠ Execution
Authorization ≠ Execution
Permission ≠ Authorization
Sandbox ≠ Authorization
```

## Deliberate exclusions

M22.8 does not:

- execute tools or plugins from `authorize()`;
- bypass `PolicyGate`;
- grant authorization from selection, argument generation, trust, lifecycle,
  permission binding, or sandbox admission alone;
- add plugin worker assignment;
- add authorization persistence or revocation;
- replace the existing confirmation provider contract.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.8 becomes VERIFIED / COMPLETE only after the user's local focused and
regression receipt passes.
