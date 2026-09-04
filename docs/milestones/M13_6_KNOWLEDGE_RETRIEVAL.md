# M13.6 — Knowledge Retrieval

## Goal

Provide deterministic retrieval of persisted personal-knowledge `Entity` values without turning retrieval into interpretation, inference, truth, authorization, or execution.

## Boundary

`KnowledgeRetriever` is a read-oriented facade over `EntityRepository`.

Retrieval can:

- fetch an entity by immutable `entity_id`
- filter entities by supported `EntityType`
- search entity IDs, canonical names, types, nested metadata, and evidence references
- report which fields matched a query
- return bounded, deterministic result sets

Retrieval does not:

- resolve or merge entity identities
- infer facts from matches
- establish truth
- mutate entities or storage
- grant authority or permission
- interpret user intent
- execute actions

## Invariants

- Retrieval ≠ Truth
- Retrieval ≠ Fact
- Search Match ≠ Fact
- Match Evidence ≠ Authority
- Retrieval ≠ Authorization
- Knowledge ≠ Policy
- Identity Resolution remains M13.2
- Persistence remains M13.5

## Determinism and bounds

Queries are bounded and normalized for case-insensitive matching. Repository ordering supplies deterministic ordering. Retrieval results have an explicit maximum size and report truncation instead of silently changing the requested limit.

## Result contract

Each `KnowledgeMatch` preserves the original immutable `Entity` and records only the retrieval fields that matched. Serialized retrieval payloads explicitly carry false authority/truth flags so downstream consumers cannot mistake presentation for authority.

## Not included

Relationship retrieval, graph traversal, inference, ranking by learned relevance, world-model integration, and runtime context integration remain later slices.
