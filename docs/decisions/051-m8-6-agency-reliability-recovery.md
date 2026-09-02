# Decision 051 — M8.6 Agency Reliability / Recovery

## Context

M8.5 can execute a bounded sequence of independently authorized execution
handoffs, but a reliable agency runtime must distinguish successful execution
from failure, interruption, partial completion, blocking, and states that
require reconciliation.

Reliability handling must not become a second authority system. In particular,
a retry must never inherit authority merely because a previous execution was
authorized.

## Decision

Introduce a provider-neutral reliability layer with three responsibilities:

```text
ExecutionObservation
        ↓
ReliabilityClassifier
        ↓
ReliabilityAssessment
        ↓
RecoveryPlanner
        ↓
RecoveryRequest
```

The classifier consumes an observed execution event plus explicit supplemental
reliability signals. It does not infer partial completion, interruption, or
retryability from successful content or model interpretation.

The planner produces bounded recovery intent as data. It never invokes the
runtime, creates an `ExecutionRequest`, mutates authorization state, schedules
a retry, or grants permission.

## Reliability classifications

```text
HEALTHY
FAILED_RETRYABLE
FAILED_TERMINAL
INTERRUPTED
PARTIAL_COMPLETION
BLOCKED
REQUIRES_RECONCILIATION
```

Explicit reconciliation, interruption, and partial-completion signals take
precedence over ordinary execution status because they indicate that the
observed state is not sufficient to treat the run as a simple terminal result.

## Recovery actions

```text
NONE
STOP
RECONCILE
REQUEST_FRESH_AUTHORIZATION
```

A retryable failure may produce `REQUEST_FRESH_AUTHORIZATION`, but that is an
instruction to re-enter the authority system, not an authorization grant.
A bounded recovery request budget prevents an implicit retry loop.

## Authority boundary

```text
Recovery ≠ Authorization
Retry ≠ Permission
Partial Completion ≠ Success
Interruption ≠ Failure
Observation ≠ Permission for the next action
```

Any new executable action must pass through the established M7 authority
chain and produce a fresh `ExecutionPreparation` before M8 execution.

## Consequences

M8 can now reason about execution reliability without altering M7 authority
semantics. Recovery remains inspectable, deterministic, bounded, and suitable
for later worker orchestration without creating hidden autonomy.
