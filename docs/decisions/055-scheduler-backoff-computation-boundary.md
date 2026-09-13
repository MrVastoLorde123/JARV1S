# Decision 055 — Scheduler Backoff Computation Boundary

Scheduler failure backoff remains bounded not only in its resulting retry multiplier but also in the computation used to derive that multiplier.

The scheduler must never construct an intermediate exponential value proportional to an untrusted or arbitrarily large persisted failure count. Backoff growth is capped before computation can become unbounded.

For ordinary failure counts, the retry sequence remains unchanged: 1x, 2x, 4x, and so on until the configured maximum multiplier is reached.

This boundary changes computation safety only. It does not change failure semantics, authorization, job lifecycle, persistence authority, resume behavior, or execution concurrency.
