# Decision 029 — Context Source Selection and Refresh

## Status

Proposed for M6.4.

## Decision

Persistent context sources are selected by a provider-neutral deterministic policy before they are treated as working-context inputs.

The selection layer is represented by `ContextSourceSelector` and does not retrieve, refresh, validate, authorize, or execute anything.

```text
Request
   ↓
ContextSourceSelector
   ↓
ContextSourceSelection
   ↓
Persistent source retrieval / refresh layer
   ↓
WorkingContextComposer
   ↓
WorkingContext
```

## Selection Rules

A persistent source is eligible when it is:

- enabled
- marked persistent
- at or above the configured relevance threshold

Eligible sources are ordered deterministically by relevance, priority, and source ID. An optional source-count limit is applied after deterministic ordering.

## Refresh Rules

Freshness is explicit.

A source with a configured refresh interval is stale when:

- it has never been refreshed, or
- the elapsed interval is greater than or equal to the configured interval.

A stale source may still be selected so that its existence is not silently hidden. However, the selection decision sets `refresh_required=True` and `authority_allowed=False`.

This establishes an important epistemic boundary:

> Stale context may remain evidence, but it is not treated as authoritative merely because it was selected.

The caller must explicitly decide how and when refresh is performed.

## Separation

This selector operates only on persistent context sources. Explicit task, execution state, execution progress, and execution observations remain separate working-context fields and are not converted into persistent sources by this policy.

`WorkingContextComposer` remains responsible for composition.

`ContextSourceSelector` does not modify `WorkingContext`, `ContextPackage`, memories, evidence, execution state, conversation state, or any external system.

## Consequences

- Source selection is deterministic and independently testable.
- Freshness is explicit rather than hidden inside retrieval or composition.
- Stale context cannot silently become authoritative.
- Future retrieval/refresh providers can be introduced behind this policy without changing working-context semantics.
- AI-assisted relevance can be introduced later as evidence or a proposal, but deterministic policy remains the enforcement boundary.
