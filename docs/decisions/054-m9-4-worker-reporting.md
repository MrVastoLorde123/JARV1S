# Decision 054 — M9.4 Worker Reporting / Result Integration

## Status

Accepted — M9.4 implementation in progress.

## Decision

Worker reports are immutable evidence about delegated work. A report must preserve worker and assignment identity, remain within the assignment output scope, and may be projected back into JARVIS WorkingContext as an `OBSERVATION`.

Reporting does not create or mutate authorization, select providers, invoke tools, or establish truth.

## Flow

```text
Bounded Worker Runtime
        ↓
WorkerReport
        ↓
WorkerReportStore
        ↓
WorkerReportIntegrator
        ↓
WorkingContext OBSERVATION
```

## Invariants

```text
Worker Output ≠ Truth
Worker Report ≠ Authorization
Reporting ≠ Authority
Evidence ≠ Permission
Output Scope ≠ Global Context
```

Every future executable action must still traverse the established M7 → M8 authority and execution path.
