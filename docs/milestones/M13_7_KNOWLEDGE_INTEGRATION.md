# M13.7 — Knowledge Integration

## Goal

Compose the M13 personal-knowledge primitives behind one knowledge-facing boundary without introducing a second semantic engine.

## Composition

```text
Entity Persistence
       ↓
Knowledge Retrieval
       ↓
Knowledge Runtime
       ├── Entities
       ├── Relationships
       └── Evidence-Backed Associations
```

## Contract

`KnowledgeRuntime` composes existing entity persistence and retrieval with immutable relationship and association collections. It exposes read/query operations and functional integration methods that return new runtime values rather than mutating prior state.

An association may only be integrated when its relationship is already present in the runtime. This preserves explicit relationship identity and prevents detached evidence from silently creating knowledge.

## Invariants

- Knowledge Integration ≠ Semantic Reasoning
- Integration ≠ Truth
- Retrieval ≠ Inference
- Association ≠ Fact
- Knowledge ≠ Policy
- Knowledge ≠ Authorization
- Knowledge ≠ User Intent
- Stored State ≠ Truth
- Existing Entity boundaries remain authoritative for entity validation.
- Integration does not resolve identities.
- Integration does not infer missing relationships.
- Integration does not execute actions.
- Integration does not grant permissions.

## Snapshot

`KnowledgeSnapshot` provides an immutable, deterministic projection of the integrated entity, relationship, and association state. Serialization preserves the non-authoritative boundaries of every contained primitive.

## Not included

Relationship persistence, association persistence, inference, entity merging, world-model construction, runtime context injection, and proactive agency remain later work.
