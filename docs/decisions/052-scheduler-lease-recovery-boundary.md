# Decision 052 — Scheduler Lease Recovery

Scheduler claims are leased, not permanent. An active lease blocks a concurrent claim; an expired lease (`lease_until <= now`) may be reclaimed by the injected store with a new claim token.

Lease recovery only restores scheduling coordination. It does not resume waiting jobs, grant authorization, mutate job state directly, or create another execution path.
