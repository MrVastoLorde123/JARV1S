# Decision 049 — Durable Reasoning Run Loop

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a host-neutral bounded run loop over the persisted M64 reasoning pulse. A run continues while the job remains runnable, records every pulse through the existing persistence boundary, and stops when the job reaches a waiting/paused or terminal state or the explicit pulse budget is exhausted.

The loop never resumes waiting state implicitly, never bypasses confirmation, and never creates a second tool-execution path.
