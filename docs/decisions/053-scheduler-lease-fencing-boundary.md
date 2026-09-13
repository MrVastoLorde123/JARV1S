# Decision 053 — Scheduler Lease Fencing

A scheduler lease grants temporary ownership of a due schedule. Lease expiry permits another worker to reclaim that ownership, so completion must be fenced by the claim token that was granted to the worker.

The injected schedule store therefore owns an atomic `complete_claim(schedule, claim_token, replacement)` boundary. It must reject completion when the stored claim no longer matches the supplied token.

A rejected completion is coordination loss, not execution success or failure. The scheduler must not perform a fallback `save` or `delete` after a rejected claim completion, because the worker is no longer authorized to mutate that schedule.

Lease fencing does not authorize actions, resume waiting jobs, mutate job state directly, or create another execution path. It only prevents stale scheduler workers from overwriting a schedule reclaimed by a newer owner.
