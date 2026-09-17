# Phase 5 — Persistent Intelligence

## Objective

Give JARVIS a coherent persistent-intelligence layer that can retain experience, structured knowledge, reusable procedures, bounded working context, and a provenance-backed personal model without turning memory into truth, authority, authorization, or execution.

## Milestones

- M83 — Canonical Persistent Memory Contract
- M84 — Provenance and Evidence Lineage
- M85 — Episodic Memory
- M86 — Semantic Knowledge
- M87 — Procedural Memory
- M88 — Working Memory
- M89 — Personal Model
- M90 — Memory Lifecycle and Consolidation Proposals
- M91 — Persistent Intelligence System and Runtime Boundary

## Architecture

```text
Experience / Evidence
        |
        v
Provenance + Persistent Memory Contract
        |
        +--> Episodic Memory
        +--> Semantic Knowledge
        +--> Procedural Memory
        +--> Working Memory
        |
        v
Personal Model
        |
        v
Lifecycle / Consolidation Proposals
        |
        v
Persistent Intelligence System
        |
        v
Existing Context / Reasoning / Planning / Authority Boundaries
```

## Non-authority rules

Memory is evidence-bearing state. Provenance identifies supporting sources. Confidence expresses uncertainty; it does not establish certainty. Personal-model entries are remembered claims, not inferred authorization or user intent. Procedural memory describes reusable knowledge but cannot execute a procedure. Consolidation is proposal-only. Working memory is contextual and cannot be persisted through the durable repository.

The Phase 5 runtime seam is provider-neutral and exposes no authorization, execution, provider-selection, or capability-invocation surface.

## Persistence

The canonical Phase 5 repository uses SQLite and the existing JARVIS database location by default. Persistent records require at least one provenance reference and immutable identity semantics. Repeated identical writes are idempotent; conflicting reuse of a memory or provenance identifier is rejected.

## Verification gate

Phase closure requires one consolidated local receipt containing the focused Phase 5 suite, the Phase 5 structural verifier, the UI production build, and the full core regression suite. A passing remote implementation alone does not close the phase.
