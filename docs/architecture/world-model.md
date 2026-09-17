# JARVIS World Model Architecture

## Purpose

The World Model is the derived state layer between evidence-bearing knowledge and cognitive reasoning. It represents entities, relationships, temporal validity, and current circumstances without becoming a source of truth or authority.

## State flow

```text
Observation + Provenance
        |
        v
Candidate Entity / Relation State
        |
        v
Temporal Validity Filter
        |
        v
Deterministic Current-View Selection
        |
        +----> Conflict Set (retained)
        |
        v
Immutable WorldSnapshot
        |
        v
Provider-neutral Context Projection
```

## Entity and relation semantics

A world entity is an immutable state candidate identified by `entity_id`. A relation is an immutable directed state candidate identified by `relation_id`. Both carry bounded confidence and provenance identifiers.

State candidates may disagree. The model does not collapse disagreement into truth; it selects a deterministic candidate for a current projection and retains a `WorldConflict` describing the competing active candidates.

## Temporal semantics

Every state candidate carries an explicit validity window. Snapshot generation uses the requested generation timestamp to exclude states that are not currently valid. Historical observations remain available even after retraction or expiry.

## Observation semantics

An observation must carry at least one provenance identifier and exactly one entity or relation assertion. Retractions are separate observations and reference a prior observation id. Identical observation ids are idempotent; conflicting reuse of an observation id is rejected.

## Snapshot semantics

`WorldSnapshot` is immutable and includes:

- selected current entity states
- selected current relation states
- explicit conflicts
- contributing observation identifiers
- deterministic snapshot identity

The snapshot is suitable for downstream context assembly. Its projection explicitly reports that it establishes neither truth nor authority.

## Runtime boundary

`JarvisRuntime` may receive a `WorldModelSystem` dependency and expose it as contextual state. The runtime seam does not grant authorization, execute capabilities, mutate external state, persist world-model state, establish truth, establish certainty, or select a provider.
