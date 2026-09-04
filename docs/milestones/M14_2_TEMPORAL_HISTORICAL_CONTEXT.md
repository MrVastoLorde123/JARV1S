# M14.2 — Temporal / Historical Context

## Goal

Represent bounded historical `ContextState` snapshots so JARVIS can distinguish what was recorded before from what is currently relevant.

## Composition

```text
ContextState snapshots
        ↓
TemporalContext
        ├── before
        ├── between
        ├── after
        └── latest
```

## Contract

`TemporalContext` stores immutable `ContextState` snapshots that have explicit ISO-8601 observation times. History is append-only at the value level: `append()` returns a new history rather than mutating an existing one.

Historical queries are deterministic and bounded. `latest` identifies the newest recorded snapshot in the collection; it does not assert that the snapshot remains true or current in the external world.

## Invariants

- History ≠ Truth
- Observation ≠ Fact
- Past State ≠ Current State
- Temporal Ordering ≠ Causality
- Historical Context ≠ User Intent
- Temporal Context ≠ Authorization
- Temporal Context ≠ Policy
- Temporal Context ≠ Execution Permission
- No temporal query mutates stored snapshots.
- No temporal query resolves identity or infers missing events.

## Not included

Goal/project context, situational context, cross-domain context, relevance prioritization, world-model integration, and runtime context injection remain later M14 slices.
