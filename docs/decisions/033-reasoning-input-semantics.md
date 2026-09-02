# Decision 033 — Reasoning Input Semantics

## Status

Proposed as M7.1.

## Context

JARVIS now assembles a canonical `WorkingContext` through source selection,
source resolution, working-context composition, and the live conversation
runtime. The next boundary is reasoning over that context.

The reasoning layer must not silently collapse observations, evidence,
persisted memory, current state, model-derived conclusions, and proposed
actions into one undifferentiated pool of truth.

## Decision

M7.1 introduces a provider-neutral semantic projection:

```text
WorkingContext
     |
     v
ReasoningContextProjector
     |
     v
ReasoningContext
```

`WorkingContext` remains canonical. `ReasoningContext` is a semantic view for
reasoning consumers; it does not retrieve, refresh, mutate, authorize, or
execute anything.

### Epistemic roles

Incoming reasoning inputs may be:

- `OBSERVED` — directly observed runtime information, such as a verified
  execution observation.
- `EVIDENCE` — supporting information represented as evidence.
- `PERSISTED_CLAIM` — information persisted in memory/history that may be
  relevant but is still a claim rather than a fresh observation.
- `CURRENT_STATE` — state currently associated with the conversation, task, or
  execution lifecycle.

`DERIVED` and `PROPOSED` are reserved for future reasoning outputs. The input
contract rejects them so model conclusions cannot silently re-enter the system
as authoritative context.

### Authority

Authority is explicitly represented by `authority_allowed`.

Authority is not inferred from model confidence. A stale source cannot be
marked authoritative. Persistent context without an explicit source-selection
decision is non-authoritative at the reasoning boundary.

### Freshness

Freshness is explicit and independent of relevance or confidence:

- `FRESH`
- `STALE`
- `UNKNOWN`

A selected source marked for refresh becomes `STALE` in the reasoning
projection and loses authority until a later deterministic refresh path
updates the source decision.

### Confidence and relevance

`relevance_score`, `confidence`, and `importance` remain descriptive signals.
They are not themselves truth or authorization decisions.

## Invariants

1. `WorkingContext` remains the canonical assembled context.
2. Projection does not retrieve, refresh, mutate, authorize, or execute.
3. `DERIVED` and `PROPOSED` cannot be used as incoming reasoning inputs.
4. Stale information cannot be authoritative.
5. Observations remain distinct from persisted claims and evidence.
6. Authority is explicit and cannot be obtained merely by increasing model
   confidence.
7. Provider-neutral serialization does not assume a model vendor, prompt
   format, or reasoning API.
8. Reasoning outputs remain proposals/derivations until deterministic
   downstream boundaries validate and authorize them.

## Consequence

JARVIS can now evolve reasoning independently from context acquisition and
execution authority. Future milestones can define interpretation,
prioritization, and proposal contracts without changing what `WorkingContext`
means or allowing a reasoning provider to become another orchestration layer.
