# Decision 039 — Policy Evaluation Semantics

## Status

M7.7 — Policy Evaluation

## Decision

Policy evaluation converts a canonical, validated `PolicyInput` into one explicit policy outcome. Policy evaluation is deterministic, provider-neutral, and has no execution capability.

```text
PolicyInput
    ↓
PolicyEvaluator
    ↓
PolicyDecision
    ↓
Confirmation / execution boundary
```

## Outcomes

- `ALLOW`
- `DENY`
- `REQUIRE_CONFIRMATION`

## Rules

1. Policy evaluation accepts only `PolicyInput` values.
2. A policy input must already represent `VALID` consequence validation.
3. `DENY` is a hard policy stop for downstream authorization flow.
4. `ALLOW` does not execute, invoke, or select tools and does not mean the user has confirmed an action.
5. `REQUIRE_CONFIRMATION` does not itself grant permission; it routes the proposal toward confirmation.
6. Action characteristics are descriptive policy facts, not model authority.
7. Irreversible, external-communication, and state-changing effects require confirmation.
8. No-effect consequences may be allowed by the default policy.
9. Policy decisions preserve request, proposal identity, validation identity, and rule provenance.
10. Policy evaluation does not mutate input, context, or system state.

## Initial deterministic policy

```text
validation_status != VALID          → DENY
IRREVERSIBLE                         → REQUIRE_CONFIRMATION
EXTERNAL_COMMUNICATION              → REQUIRE_CONFIRMATION
STATE_CHANGE                        → REQUIRE_CONFIRMATION
NONE                                → ALLOW
```

## Non-goals

M7.7 does not request confirmation, execute actions, select tools, invoke providers, or mutate state.
