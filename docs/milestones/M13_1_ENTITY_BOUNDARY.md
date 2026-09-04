# M13.1 — Entity Boundary

## Status

IN PROGRESS

## Purpose

M13.1 defines the boundary for a persistent personal knowledge entity without implementing identity resolution, relationships, persistence, retrieval, or deep integration.

An Entity is a stable referent inside JARVIS's knowledge layer. It gives memories and evidence a structured object they may refer to, while deliberately avoiding claims of truth, intent, authority, authorization, or policy.

## Boundary

```text
Memory / Evidence
       ↓
   Entity Boundary
       ↓
Structured Referent
```

M13.1 does not perform:

- identity resolution
- entity merging or deduplication
- relationship inference
- database persistence
- knowledge retrieval
- world-model integration
- authorization or policy decisions

## Invariants

```text
Entity ≠ Truth
Entity ≠ Fact
Entity ≠ Intent
Entity ≠ Authorization
Entity ≠ Policy
Entity ≠ Memory
Identity ≠ Authority
Association ≠ Authorization
Inference ≠ Fact
Knowledge ≠ Policy
```

## Contract

An Entity contains:

- `entity_id`: stable opaque identity for the entity object
- `entity_type`: bounded ontology category
- `canonical_name`: human-readable label
- `metadata`: bounded non-authoritative attributes
- `evidence_refs`: opaque references to supporting memory/evidence records

Construction creates a referent, not a truth assertion. Evidence references record provenance/association only; they do not elevate the entity into truth.

## Design Properties

- Immutable value object.
- Deterministic serialization.
- Bounded strings and collections.
- Provider-neutral.
- Metadata and evidence references cannot be mutated through retained references.
- No authority-bearing fields.
- No execution or policy hooks.

## Planned Follow-on

M13.2 will address identity/resolution separately. M13.3 will define relationships. Persistence begins only after the boundary contracts are stable.
