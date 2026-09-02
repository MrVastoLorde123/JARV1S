# Decision 047 — M8.1 Execution Runtime

## Status

Accepted — M8.1 implementation boundary.

## Decision

M8.1 introduces a provider-neutral execution runtime downstream of M7's `READY` execution handoff.

The runtime may attempt exactly one execution through an injected `ExecutionAdapter` and returns an `ExecutionObservation` describing what actually happened.

The adapter is the integration point for concrete execution. Mapping the provider-neutral `ExecutionRequest.operation` to a concrete capability or plugin is intentionally formalized in M8.2, not in the runtime itself.

## Input boundary

Only `ExecutionPreparationStatus.READY` may reach an execution attempt.

A `BLOCKED` preparation produces a `NOT_ATTEMPTED` observation and must never invoke the adapter.

## Outcome semantics

```text
NOT_ATTEMPTED
ATTEMPTED
SUCCEEDED
FAILED
```

`ATTEMPTED` is a distinct runtime state from `SUCCEEDED`. A failed adapter result or adapter exception remains a failed execution observation.

## Authority boundary

M8.1 cannot:

- authorize an action;
- change authorization;
- bypass M7 confirmation or integrity;
- infer authorization from adapter success;
- select a capability as an authority decision;
- retry or schedule execution;
- create workers or multi-step agency.

## Provenance

Successful and failed observations preserve the M7 identity chain:

```text
proposal_id
validation_id
policy_decision_id
confirmation_id (when applicable)
authorization_id
execution_id
```

## Existing capability stack

The existing `ToolService` remains the concrete invocation service. `ToolServiceExecutionAdapter` is a compatibility adapter and is not an authority gate.

## Hard invariants

```text
READY ≠ EXECUTED
ATTEMPTED ≠ SUCCEEDED
FAILED ≠ SUCCESS
EXECUTION ≠ AUTHORIZATION
OBSERVATION ≠ AUTHORIZATION
```

## Verification rule

M8.1 cannot be closed until focused execution-runtime tests and the full repository test suite pass from a real checkout. GitHub Actions are not currently available for this repository, so connector-level file writes do not constitute test verification.
