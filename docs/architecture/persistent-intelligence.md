# Persistent Intelligence Architecture

Phase 5 establishes a single provider-neutral memory control plane over durable memory state and provenance lineage.

## Responsibilities

`PersistentMemoryRecord` is the canonical durable representation. It separates four memory forms: episodic, semantic, procedural, and working. Working memory remains contextual and is deliberately excluded from durable storage.

`ProvenanceRef` and `ProvenanceChain` identify the evidence lineage for a memory claim. A provenance digest provides deterministic lineage identity, but provenance does not establish truth.

Typed memory projections preserve domain semantics:

- episodic memory records observed events and outcomes;
- semantic memory records propositions with explicit validation status and uncertainty;
- procedural memory records reusable steps, prerequisites, capability references, and verification descriptions;
- working memory records bounded session context, assumptions, and open questions.

`PersonalModel` is a bounded projection over provenance-backed remembered entries such as preferences, goals, constraints, and interests. It is explicitly not user intent or authorization.

`MemoryTransition` enforces lifecycle rules. Consolidation produces `ConsolidationProposal` values only; it does not silently rewrite durable knowledge.

`PersistentMemoryRepository` is the durable boundary. It requires provenance for persistent records, rejects working-memory durability, performs idempotent writes, supports deterministic recall, and applies only validated lifecycle transitions.

`PersistentIntelligenceSystem` composes the above services and provides a stable runtime-facing seam.

## Existing-boundary integration

`JarvisRuntime` may receive an optional `PersistentIntelligenceSystem`. The runtime remains non-authorizing, non-executing, non-provider-selecting, and non-truth-establishing. Persistent intelligence supplies state and evidence to downstream layers; it cannot cross the existing Authority or Execution boundaries by itself.

## Trust model

```text
source -> provenance -> memory claim -> validation/confidence -> recall/context
```

At every step, evidence remains distinguishable from truth. Durable state remains distinguishable from authority. A remembered procedure remains distinguishable from an executable capability.
