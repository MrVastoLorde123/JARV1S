# M8.4 — Execution Lifecycle / Continuation

**Status:** VERIFIED / COMPLETE

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
- distinguish pending, running, completed, failed, blocked, cancelled, and continuation-required states where appropriate;
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

A continuation request remains tied to its originating execution identity and cannot silently authorize a new operation. Any distinct future action must still pass through the established M7 authority chain.

## Existing-stack relationship

M8.1 owns single-attempt execution semantics. M8.2 owns capability/plugin realization. M8.3 owns the return of execution observations into context/state. M8.4 adds lifecycle state around these events without replacing those responsibilities.

M8.4 is intentionally distinct from the existing plan-level execution state model: it represents the lifecycle of an individual execution and does not replace or duplicate plan execution status.

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

## Implemented semantics

`ExecutionLifecycleStatus` provides explicit states for pending, running, succeeded, failed, blocked, cancelled, and continuation-required executions.

`ContinuationRequest` is immutable, identity-bound data. It contains no tool handle, provider handle, or authorization grant.

Lifecycle transitions are immutable and explicit:

```text
PENDING → RUNNING
RUNNING + SUCCEEDED observation → SUCCEEDED
RUNNING + FAILED observation → FAILED
RUNNING + NOT_ATTEMPTED observation → BLOCKED
RUNNING / FAILED → CONTINUATION_REQUIRED
CONTINUATION_REQUIRED → PENDING   (consume only; no authorization)
non-terminal → CANCELLED
```

Terminal states cannot silently continue or be cancelled. Observation identity must match `execution_id`. Context projection exposes lifecycle information as state, never as an authority grant.

## Verification

Verified from the user's real checkout:

```text
python -m unittest src.agency.tests.test_execution_lifecycle -v
Ran 11 tests in 0.004s
OK

python -m unittest
Ran 925 tests in 5.353s
OK
```

M8.4 is therefore verified complete on `feature/m8-4-execution-lifecycle-continuation`.
