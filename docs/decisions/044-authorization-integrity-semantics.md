# Decision 044 — Authorization Integrity Semantics

## Status

M7.9.1 — Authorization Integrity

## Decision

Authorization is a distinct semantic artifact that must remain bound to the exact policy decision that produced it. When policy required confirmation, an authorized decision must also remain bound to the exact confirmed confirmation result and valid confirmation-integrity chain.

```text
PolicyDecision
    ↓
AuthorizationDecision
    ↓
AuthorizationIntegrityValidator
    ↓
AuthorizationIntegrity
    ↓
Execution boundary
```

## Rules

1. Authorization integrity validates exact request, proposal identity, validation identity, and policy-decision identity.
2. Authorization integrity preserves the authorization identity.
3. `ALLOW` authorization must not acquire confirmation identity.
4. `REQUIRE_CONFIRMATION` authorization must be backed by a terminal `CONFIRMED` result and valid confirmation integrity.
5. A confirmation artifact from another policy decision is invalid for the current authorization.
6. Integrity validity does not itself grant authorization.
7. Authorization integrity does not execute, select tools, invoke providers, or mutate state.
8. Authorization integrity findings are first-class and deterministic.

## Non-goals

M7.9.1 does not execute actions, select tools, invoke providers, mint execution handles, or mutate state.
