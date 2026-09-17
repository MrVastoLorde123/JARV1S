# Decision — Phase 5 Persistent Intelligence

## Decision

Adopt one canonical provenance-first persistent-intelligence boundary rather than extending the older memory tables with unrelated ad hoc semantics.

The canonical model distinguishes:

- durable memory identity and lifecycle;
- provenance/evidence lineage;
- episodic, semantic, and procedural representations;
- bounded working memory;
- a provenance-backed personal model;
- proposal-only consolidation;
- one durable repository and one provider-neutral composition root.

## Why

The existing JARVIS code already contains durable memory, evidence, retrieval, and context contracts. Those components provide useful foundations but do not form one coherent persistent-intelligence boundary. Phase 5 therefore adds a typed contract and composition root while keeping existing authority and execution boundaries intact.

## Rejected alternatives

### Treat memory as truth
Rejected. A memory record is retained evidence-bearing state with confidence and provenance. It cannot establish certainty by itself.

### Let memory authorize behavior
Rejected. Remembered preferences, goals, constraints, and procedures are inputs to reasoning and planning, not authorization.

### Let consolidation mutate knowledge automatically
Rejected. Consolidation creates explicit proposals from repeated evidence. A later boundary must decide whether a proposal is accepted and persisted.

### Persist working memory as durable memory
Rejected. Working memory is session/context state and has different lifecycle semantics from durable memory.

## Boundary conditions

Phase 5 does not select an AI provider, invoke capabilities, authorize execution, execute procedures, establish truth, or independently grant permission. It can store and retrieve evidence-backed state only through its defined persistence contract.
