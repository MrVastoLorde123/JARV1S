# M13.2 — Entity Identity / Resolution

## Purpose

M13.2 determines whether a textual reference is sufficiently aligned with one or more existing `Entity` candidates to be treated as the same referent for knowledge workflows.

Identity resolution is a bounded judgment. It does not establish truth, merge entities, mutate entities, infer intent, grant authority, authorize execution, or persist state.

## Model

```text
reference
   ↓
normalization
   ↓
candidate comparison
   ↓
deterministic score + reasons
   ↓
EXACT_MATCH / POSSIBLE_MATCH / NO_MATCH / CONFLICT
```

## Signals

The first resolver is deliberately deterministic and explainable:

- canonical-name normalization and exact/containment comparison
- optional expected entity-type compatibility
- explicit metadata aliases
- stable score ordering and entity-id tie-breaking

## Resolution statuses

`EXACT_MATCH` means the configured evidence reached the exact threshold. It is still an identity-resolution judgment, not a truth guarantee.

`POSSIBLE_MATCH` means bounded evidence supports a likely correspondence but does not justify exact resolution.

`NO_MATCH` means available evidence did not meet the configured threshold.

`CONFLICT` means multiple candidates share the highest qualifying score and the resolver refuses to select one deterministically.

## Walls

```text
Identity Resolution ≠ Truth
Identity Resolution ≠ Fact
Identity Resolution ≠ Intent
Identity Resolution ≠ Authorization
Identity Resolution ≠ Policy
Identity Resolution ≠ Entity Mutation
Identity Resolution ≠ Persistence
Similarity ≠ Certainty
Ambiguity ≠ Permission
```

## Explicit non-goals

M13.2 does not:

- merge, delete, rename, or mutate entities
- persist identity decisions
- create relationships
- declare evidence true
- use an AI provider as an authority source
- authorize or execute actions
- resolve arbitrary real-world identity from weak signals

## Verification target

The resolver must remain deterministic, immutable at the result boundary, bounded in input size, explainable through reasons, and incapable of carrying authority semantics.
