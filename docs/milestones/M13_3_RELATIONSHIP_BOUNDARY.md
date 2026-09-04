# M13.3 — Relationship Boundary

## Goal

Define a bounded representation for associations between personal-knowledge entities.

## Boundary

A `Relationship` connects two entity identities with an explicit relationship type, optional metadata, and evidence references.

A relationship is an association. It is not, by itself, a truth claim or fact. Evidence references identify supporting material but do not become authority through the relationship object.

## Supported relationship types

- `works_on`
- `owns`
- `knows`
- `depends_on`
- `uses`
- `located_at`
- `related_to`
- `part_of`
- `learned_from`
- `supports`
- `conflicts_with`

## Invariants

- Relationship ≠ Entity
- Relationship ≠ Truth
- Relationship ≠ Fact
- Association ≠ Authorization
- Association ≠ Policy
- Association ≠ Intent
- Evidence ≠ Authority
- Knowledge ≠ Policy
- A relationship does not mutate either endpoint entity.
- A relationship does not perform identity resolution.
- A relationship does not persist itself to storage.

## Serialization

Relationships are immutable and expose deterministic JSON-compatible serialization. Metadata is defensively frozen internally and evidence references are unique and bounded.

## Not included

Identity resolution, entity merging, evidence-backed inference, persistence, retrieval, and integration into runtime context remain later M13 slices.
