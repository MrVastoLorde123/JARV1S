# Decision 053 — Scheduler Failure Recovery

A scheduler-owned worker failure must not strand its claim until the lease naturally expires. If execution raises before producing a run result, the scheduler records the failure as an observable scheduler result and uses the existing fenced `complete_claim` boundary to release ownership into a retry schedule.

Failure recovery remains scheduler coordination only. It does not reinterpret the failure as success, mutate the autonomous job state directly, authorize actions, or bypass claim fencing.
