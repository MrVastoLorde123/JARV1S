# M7 — Deterministic Authority Pipeline

**Status: CLOSED**  
**Implementation checkpoint:** `feature/m7-10-execution-semantics`  
**Verified full suite:** 884 / 884 tests passing

## What M7 Established

M7 establishes the deterministic path from a proposed action to a provider-neutral execution handoff.

```text
Reasoning
   ↓
Interpretation
   ↓
Prioritization
   ↓
Proposal
   ↓
Validation
   ↓
Policy
   ↓
Confirmation
   ↓
Confirmation Integrity
   ↓
Authorization
   ↓
Authorization Integrity
   ↓
Execution Preparation / Handoff
```

## Final Meaning

The final M7 output means:

> The action was reasoned about, validated, policy-evaluated, confirmed when required, provenance-checked, authorized, and is ready to be handed to an execution system.

It does **not** mean that the action has executed.

## Hard Boundary

M7 does not:

- invoke tools or providers;
- access credentials;
- perform external side effects;
- execute actions;
- define worker orchestration;
- define the user interface;
- depend on a specific AI provider for authority.

## M7.10 Final Gate

`ExecutionGate` only prepares an `ExecutionRequest` when authorization is `AUTHORIZED` and authorization integrity is `VALID`.

```text
AUTHORIZED + VALID INTEGRITY
            ↓
      READY handoff
            ≠
         EXECUTED
```

## Semantic Invariants

```text
Interpretation ≠ Truth
Validation ≠ Authorization
Confirmation ≠ Authorization
Authorization ≠ Execution
Integrity ≠ Authority
READY ≠ EXECUTED
```

## Identity Chain

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

## Milestone Closure Rule

M7 is intentionally closed here. No additional M7 semantic gate is planned.

The next architectural responsibility belongs to M8: turning an authorized, integrity-valid execution handoff into controlled real execution and observable results.
