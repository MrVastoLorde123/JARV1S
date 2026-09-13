# Decision 042 — Autonomous Job Execution Pulse Boundary

## Status

Proposed V1 application-layer boundary building on M56.

## Decision

Introduce a resumable execution pulse that performs one bounded heartbeat for a persisted autonomous job.

```text
Persistent Job
   ↓
Load exact job
   ↓
Start if QUEUED / advance one cycle if RUNNING
   ↓
Persist resulting snapshot
   ↓
Return current state
```

## Contract

- The pulse loads a job by exact identity through the M56 persistence service.
- QUEUED jobs may transition to RUNNING and then execute one worker cycle.
- RUNNING jobs execute at most one worker cycle per pulse.
- Terminal jobs are returned unchanged and are not sent to the worker.
- Waiting and paused jobs are returned unchanged until their explicit dependency is cleared.
- Every changed job snapshot is persisted before the pulse returns success.
- The pulse is host-neutral and does not select a background hosting mechanism.
- The pulse does not grant authorization or create new execution authority.

## Authority walls

```text
Execution Pulse ≠ Background Host
Execution Pulse ≠ Authorization
Execution Pulse ≠ Retry Authority
Persistence ≠ Truth
```

## V1 purpose

This is the bridge between the bounded M55 loop and real asynchronous operation. An external host can invoke the pulse repeatedly while the user is away, and each invocation leaves a recoverable job snapshot behind.

## Verification

Focused pulse tests must cover queued start, running advancement, terminal no-op, waiting/paused no-op, persistence after progress, and exact job identity.
