# M14.4 — Situational Context

## Goal

Represent the bounded situation surrounding a `ContextState` using explicit observational signals.

## Composition

```text
ContextState
     +
SituationSignal[]
     ↓
SituationalContext
```

A `SituationSignal` describes an observed or supplied signal. It is not independently promoted to truth or fact. `SituationalContext` groups those signals with the contextual state they describe.

## Contract

- Signals have bounded identifiers, categories, values, and optional source references.
- Signal values are defensively frozen and limited to JSON-like structures.
- Signal IDs are unique within a situation.
- Situational context is immutable; updates return a new value.
- Lookup is deterministic and does not infer missing signals.
- Serialization preserves provenance references and non-authoritative flags.

## Invariants

- Situation ≠ Truth
- Signal ≠ Fact
- Observation ≠ Certainty
- Situational Context ≠ User Intent
- Situational Context ≠ Policy
- Situational Context ≠ Authorization
- Situation ≠ Execution Permission
- Source Reference ≠ Authority
- Signals do not mutate `ContextState`.
- Situational context does not infer causality, intent, or permission.

## Not included

Cross-domain context relevance, probabilistic inference, world-model synthesis, runtime context injection, and proactive agency remain later M14/M15 work.
