# Decision 047 — Explicit Wait-State Resume Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce an explicit resume boundary for persisted autonomous jobs. A waiting or paused job may return to `RUNNING` only through a caller-supplied resume request that matches the persisted state and carries the required explicit signal.

The resume boundary:

- restores the exact persisted job identity;
- rejects resume requests for terminal or otherwise non-resumable jobs;
- requires explicit confirmation when resuming authorization/tool waits;
- requires explicit input context when resuming an input wait;
- allows a paused job to resume only through an explicit resume request;
- persists the resumed snapshot before returning it;
- does not execute reasoning or tools itself.

## Safety boundary

Persisted waiting state is not implicit consent. Restoring a job never turns a prior proposal into authority, and resuming a job never bypasses the existing reasoning/tool/authorization boundaries.
