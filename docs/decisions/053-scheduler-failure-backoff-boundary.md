# Decision 053 — Scheduler Failure Backoff

Scheduler-owned worker failures remain observable failures and are retried through the existing fenced claim boundary.

Repeated failures increase the retry delay exponentially from the schedule interval, bounded by a deterministic maximum multiplier. Successful non-terminal execution resets the failure streak.

Failure backoff changes scheduling time only. It does not authorize actions, convert failure to success, resume waiting jobs, or create a parallel execution path.
