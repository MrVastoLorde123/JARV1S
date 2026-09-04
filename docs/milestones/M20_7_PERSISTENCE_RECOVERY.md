# M20.7 — Persistence / Recovery

## Purpose

M20.7 makes the M20 long-horizon state durable as an explicit immutable snapshot and defines safe recovery semantics.

The core invariant is:

> JARVIS may recover what was persisted, but recovery must never invent continuity, progress, outcome truth, authorization, or execution.

## Persisted state

A `PersistenceSnapshot` captures:

- snapshot identity and schema version
- goal and objective identity/state/provenance
- immutable task definitions and lifecycle state
- task dependency edges
- complete progress evidence
- evaluated progress derived from that evidence
- plan identity and status

Serialization is deterministic JSON.

## Recovery

`recover_snapshot()` accepts a JSON string or mapping and validates:

1. schema version
2. authority metadata
3. goal/objective/task identities
4. dependency references
5. evidence identities and task ownership
6. persisted evaluations against recovered evidence
7. reconstructed plan status against persisted plan status

A failed validation raises `PersistenceError`; malformed or contradictory state is never silently repaired.

## Persistence store

`PersistenceStore` provides an immutable-by-replacement, conflict-aware snapshot registry. Re-registering the exact same snapshot is idempotent. Reusing an existing snapshot identity for different content is rejected.

## Authority boundary

Persistence and recovery are state-management operations only.

- Persistence ≠ Authorization
- Recovery ≠ Authorization
- Recovered State ≠ User Intent
- Recorded State ≠ Observed Reality
- Observed Progress ≠ Outcome Truth
- Recovery ≠ Execution
- Snapshot Identity ≠ Authority

Recovered payloads explicitly reject any persisted authority, authorization, or execution flags.

## Deliberate exclusions

M20.7 does not perform task execution, scheduling, worker assignment, plugin assignment, autonomous continuation, authorization, or business-outcome truth evaluation.

## Verification target

Focused M20.7 tests must pass together with the complete existing core regression suite before the milestone is marked verified.
