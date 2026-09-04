# M13.5 — Entity Persistence

## Goal

Persist personal-knowledge `Entity` values durably and retrieve them without changing their semantic or authority boundaries.

## Boundary

`EntityRepository` stores and reconstructs immutable `Entity` values using SQLite. Persistence is storage, not interpretation.

An entity loaded from storage remains:

- an entity, not truth
- an entity, not a fact
- an entity, not intent
- an entity, not authorization
- an entity, not policy
- an entity, not execution permission

## Persistence contract

- Storage is keyed by immutable `entity_id`.
- Duplicate entity IDs are rejected rather than silently overwritten.
- Reads reconstruct the canonical `Entity` type so normal validation is reapplied.
- Metadata and evidence references round-trip through JSON.
- Listing is deterministic by `entity_id`.
- Missing entities are distinguishable from persistence corruption.
- Delete is an explicit storage operation and does not mutate an existing in-memory `Entity` value.
- SQL values are parameterized; entity values are not interpreted as SQL.

## Invariants

- Persistence ≠ Truth
- Persistence ≠ Fact
- Storage ≠ Authority
- Retrieval ≠ Authorization
- Database State ≠ User Intent
- Entity Identity ≠ Authority
- Stored data must satisfy the existing Entity boundary when reconstructed.

## Not included

Relationship persistence, association persistence, knowledge retrieval/search, inference, entity merging, and runtime context integration remain later M13 slices.
