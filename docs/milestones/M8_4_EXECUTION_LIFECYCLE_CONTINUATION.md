# M8.4 — Execution Lifecycle / Continuation

**Status:** IMPLEMENTATION IN PROGRESS

## Purpose

M8.4 defines lifecycle and bounded continuation semantics for executions that span time or require explicit continuation after an execution result.

```text
ExecutionRequest
      ↓
Lifecycle State
      ↓
Execution / Observation
      ↓
Continuation Decision
      ↓
Next Lifecycle State
```

## Responsibilities

- represent explicit lifecycle state for an execution;
- distinguish pending, running, completed, failed, cancelled, and continuation-required states where appropriate;
- preserve `execution_id` across the lifecycle;
- represent continuation as an explicit state transition rather than an implicit retry;
- keep continuation bounded by explicit inputs and lifecycle rules;
- prevent continuation from creating new authorization;
- provide deterministic lifecycle transitions suitable for later multi-step agency.

## Authority boundary

Lifecycle state describes where an execution is in its controlled process. It does not grant authority.

```text
Continuation ≠ Authorization
Lifecycle ≠ Policy
Lifecycle ≠ Retry Permission
Observation ≠ Permission for the next action
```

A continuation request must remain tied to its originating execution identity and cannot silently authorize a new operation. Any distinct future action must still pass through the established M7 authority chain.

## Existing-stack relationship

M8.1 owns single-attempt execution semantics. M8.2 owns capability/plugin realization. M8.3 owns the return of execution observations into context/state. M8.4 adds lifecycle state around these events without replacing those responsibilities.

## Explicit non-goals

M8.4 does not implement:

- autonomous multi-step planning;
- unrestricted retries;
- recovery policy;
- worker actors;
- policy or authorization decisions;
- dynamic plugin loading;
- natural-language capability selection.

Those concerns belong to M8.5/M8.6 or the established authority layers.

## Initial invariants

```text
execution identity is stable across lifecycle transitions
state transitions are explicit
terminal states do not silently continue
continuation is bounded and represented as data
continuation does not grant authority
new actions require the M7 authority chain
```

## Verification

Verification is pending until focused M8.4 tests and the full repository `unittest` suite pass from the user's real checkout.
