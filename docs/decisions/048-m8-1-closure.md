# ADR 048 — M8.1 Execution Runtime Closure

**Status:** Accepted

## Decision

M8.1 is closed after real local verification of the canonical `feature/m8-1-execution-runtime` branch.

The verified M8.1 implementation consumes only `READY` M7 execution preparations, delegates one execution attempt through an injected adapter, and returns a structured provider-neutral execution observation.

## Verification Record

- Focused M8.1 tests: **8 / 8 passed**
- Full repository suite: **892 / 892 passed**
- Full-suite runtime: **6.832s**
- Test framework: repository-native `unittest`

## Boundary

M8.1 does not perform capability discovery/selection, policy, confirmation, authorization, observation-store integration, retries, scheduling, workers, multi-step agency, or UI/provider orchestration.

`ExecutionRequest.operation` remains provider-neutral. The formal capability/plugin mapping is deferred to M8.2.

## Invariants

- `READY` permits an execution attempt but does not imply success.
- `BLOCKED` preparations are never invoked.
- `ATTEMPTED` is distinct from `SUCCEEDED`.
- `FAILED` remains a failure observation.
- Execution cannot grant, change, or infer authorization.
- Execution observations preserve the M7 identity chain.

## Consequence

M8.2 — Capability / Plugin Execution Boundary may begin from the verified M8.1 state.
