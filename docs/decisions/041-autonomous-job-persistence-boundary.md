# Decision 041 — Autonomous Job Persistence Boundary

## Status

Proposed V1 application-layer persistence boundary building on M55.

## Decision

Introduce an explicit persistence service for autonomous jobs. The service persists immutable job snapshots through an injected store and can restore a job by identity after process restart.

```text
Autonomous Job
    ↓
M56 Persistence Service
    ↓
Injected Job Store
    ↓
Durable Job Snapshot
```

## Contract

- Only an `AutonomousJob` snapshot may be persisted.
- Persistence requires an explicitly injected store; no storage technology is selected here.
- The exact immutable job snapshot is passed to the store without reinterpretation.
- A successful store operation must return a non-empty revision/record identifier.
- Restoration is by exact job identity and rejects a store result for a different job.
- Persistence failures are surfaced; the service does not fabricate success.
- Persistence does not grant authority, authorization, execution permission, truth, retry authority, or policy authority.
- A persisted job remains resumable only according to its own lifecycle state; persistence does not change job state.

## Authority walls

```text
Job Persistence ≠ Job Execution
Job Persistence ≠ Authorization
Job Persistence ≠ Retry Authority
Persisted State ≠ Semantic Truth
Storage Backend ≠ Policy Authority
```

## V1 purpose

This boundary makes an autonomous job recoverable across process restarts. Later scheduling/background-host work can load persisted jobs and resume only those whose lifecycle permits resumption.

## Verification

Focused persistence tests must demonstrate exact snapshot forwarding, explicit store binding, stable receipt identity, restoration, mismatched-identity rejection, and preserved authority walls.
