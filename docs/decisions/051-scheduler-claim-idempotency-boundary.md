# Decision 051 — Scheduler Claim/Idempotency Boundary

## Decision

A due schedule must be atomically claimed before a runtime pulse is executed.

The claim is represented by an opaque lease token with an expiry time. A second scheduler observing the same due entry while the lease is live must not execute the job.

The scheduler releases the claim by replacing the entry with the next due schedule or deleting it for terminal/waiting jobs.

Claiming is coordination only. It does not grant authorization, resume waiting state, or create a tool execution path.
