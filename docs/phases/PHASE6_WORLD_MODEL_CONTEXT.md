# Phase 6 — World Model / Current Context

## Objective

Give JARVIS an explicit, evidence-backed representation of entities, relationships, temporal state, and current circumstances between persistent intelligence and downstream reasoning/context composition.

The phase derives a bounded current view from observations. It does not turn observations into truth, and it does not introduce authority or execution power.

## Milestones

- M92 — Canonical World-State Contract
- M93 — Entity and Relationship State Model
- M94 — Temporal Validity Model
- M95 — Provenance-Bound Observation Ingestion
- M96 — Deterministic Reconciliation and Conflict Retention
- M97 — Immutable World Snapshot / Current Context Projection
- M98 — World-Model System Lifecycle Boundary
- M99 — Runtime Integration Boundary

## Architecture

```text
Persistent Intelligence / Evidence
             |
             v
      World Observation
             |
      +------+------+
      |             |
   Entities      Relations
      |             |
      +------+------+
             v
     Temporal Validity
             |
             v
   Reconciliation / Conflicts
             |
             v
     Immutable Snapshot
             |
             +------> Current Context
             |
             v
     Reasoning / Planning
```

## Epistemic rules

- Observation is evidence, not truth.
- A selected current candidate is a context-selection result, not a truth claim.
- Conflicting active candidates remain visible as explicit ambiguity.
- Confidence is bounded uncertainty, not certainty.
- Temporal validity is explicit; expired assertions do not enter the current view.
- Retraction removes an observation from the current view without erasing its historical record.
- Snapshot generation is deterministic for identical observation state and generation time.

## Authority boundary

The Phase 6 subsystem does not authorize work, execute capabilities, mutate external state, select providers, establish truth, or establish certainty. Runtime integration exposes the world model as contextual state only.

## Persistence boundary

The world model is a derived in-memory view over evidence-bearing observations. Durable truth claims are intentionally not introduced here; Phase 5 remains the provenance-backed durable evidence layer.

## Verification gate

Phase closure requires one consolidated local receipt containing the focused Phase 6 suite, the Phase 6 structural verifier, the UI production build, and the full core regression suite. A passing remote implementation alone does not close the phase.
