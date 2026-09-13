# Decision 050 — Persistent Runtime Scheduler Boundary

## Status
Proposed V1 runtime boundary.

## Decision
Introduce a host-neutral scheduler that stores bounded execution intents and invokes the existing persisted reasoning run loop only when an intent is due.

The scheduler:
- persists schedule identity and next due time through an injected store;
- invokes at most one bounded pulse per scheduled tick;
- never resumes waiting jobs automatically;
- removes terminal jobs from future scheduling;
- re-schedules runnable jobs using an explicit interval;
- does not grant authorization, choose providers, or execute tools directly.

Scheduling is coordination, not authority. A due schedule is not permission to bypass the job's persisted state or existing tool gates.
