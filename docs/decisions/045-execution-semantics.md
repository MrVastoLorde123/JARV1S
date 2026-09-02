# Decision 045 — Execution Semantics

## Status

M7.10 — Execution Semantics

## Decision

M7 ends at a provider-neutral execution boundary. An action becomes eligible
for handoff only when its authorization decision is `AUTHORIZED` and its
authorization integrity is `VALID`. The resulting `ExecutionRequest` is a
semantic handoff envelope; it is not itself a tool invocation or side effect.

```text
AuthorizationDecision
        ↓
AuthorizationIntegrity
        ↓
ExecutionGate
        ↓
ExecutionPreparation
        ↓
ExecutionRequest
        ↓
M8 execution adapter / tool boundary
```

## Rules

1. Execution preparation requires an `AUTHORIZED` authorization decision.
2. Execution preparation requires `VALID` authorization integrity.
3. Authorization and authorization-integrity identities must remain aligned.
4. The `execution_id` is a distinct downstream semantic identity.
5. An execution request preserves request, proposal, validation, policy-decision, confirmation, and authorization provenance.
6. Execution requests are provider-neutral and do not contain tool handles, provider selectors, credentials, invocation controls, or authorization controls.
7. Blocked preparation produces no execution request.
8. `READY` means eligible for downstream execution handoff; it does not mean executed, completed, or successful.
9. M7.10 performs no tool selection, provider invocation, credential access, external side effect, or state mutation.
10. Actual execution adapters and result/error lifecycle semantics belong to M8.

## Identity chain

```text
proposal_id
    ↓
validation_id
    ↓
policy_decision_id
    ↓
confirmation_id       (when required)
    ↓
authorization_id
    ↓
execution_id
```

## Boundary invariant

```text
AUTHORIZED + VALID INTEGRITY
    ↓
READY execution handoff
    ≠
executed
```

## M7 closure

With M7.10 complete, M7 establishes the deterministic semantic authority chain
from proposal through validation, policy, confirmation, authorization, and the
final execution handoff boundary. M8 may implement concrete execution adapters
without changing these authority semantics.
