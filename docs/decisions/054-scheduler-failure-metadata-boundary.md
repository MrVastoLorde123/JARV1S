# Decision 054 — Scheduler Failure Metadata

The runtime scheduler persists the most recent worker-failure metadata with the retry schedule so failure context survives the scheduling boundary.

A failed worker execution remains an observable failure. The scheduler records a deterministic failure reason and failure timestamp alongside the existing failure streak and backoff state.

Successful non-terminal execution clears prior failure metadata and resets the failure streak.

Failure metadata is diagnostic state only. It does not authorize actions, change job lifecycle state, resume waiting jobs, or create another execution path.
