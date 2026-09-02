# M8.1 — Execution Runtime

**Status:** IMPLEMENTED — VERIFICATION PENDING

## Purpose

M8.1 is the first agency runtime downstream of the M7 authority boundary. It consumes a valid `READY` `ExecutionPreparation`, attempts one execution through an injected adapter, and returns a structured `ExecutionObservation`.

## Flow

```text
M7 READY ExecutionPreparation
            ↓
      ExecutionRuntime
            ↓
      ExecutionAdapter
            ↓
      ExecutionOutcome
            ↓
    ExecutionObservation
```

## Responsibilities

- accept only `READY` preparations for execution attempts;
- keep blocked preparations explicitly `NOT_ATTEMPTED`;
- delegate concrete execution to an injected adapter;
- distinguish attempted, succeeded, and failed execution;
- preserve M7 identity/provenance through `execution_id`;
- represent adapter failures as execution observations.

## Non-responsibilities

M8.1 does not own capability discovery or selection, policy, confirmation, authorization, observation-store integration, retries, scheduling, workers, multi-step agency, or UI/provider orchestration.

## Boundary with M8.2

`ExecutionRequest.operation` remains provider-neutral. The generic runtime does not decide which capability or plugin implements it. Concrete mapping is an adapter concern and its formal capability/plugin boundary is M8.2.

## State semantics

| State | Attempted | Completed | Succeeded |
| --- | ---: | ---: | ---: |
| `NOT_ATTEMPTED` | No | No | No |
| `ATTEMPTED` | Yes | No | No |
| `SUCCEEDED` | Yes | Yes | Yes |
| `FAILED` | Yes | Yes | No |

## Verification

Focused tests have been added under `src/agency/tests/test_execution_runtime.py`.

The milestone remains open until the focused tests and the full repository suite are run successfully from a real checkout. The repository currently has no GitHub Actions workflow runs available, so source writes alone are not treated as verification.
