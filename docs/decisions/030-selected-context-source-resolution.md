# Decision 030 — Selected Context Source Resolution

## Status

Proposed for M6.5.

## Decision

Persistent context may enter `WorkingContext` only through an explicit selection-to-resolution path.

```text
Request
   ↓
ContextSourceSelector
   ↓
ContextSourceSelection
   ↓
ContextSourceResolver
   ↓
Resolved ContextItems
   ↓
WorkingContextComposer
   ↓
WorkingContext
```

`ContextSourceSelector` remains responsible only for deterministic eligibility and freshness decisions. `ContextSourceResolver` may materialize only source IDs present in the selection.

## Enforcement

When selected sources are resolved into a working context:

- persistent retrieval performed by the ordinary builder is disabled for that composition path
- only explicitly resolved persistent items are inserted
- every resolved persistent item must carry `provenance.source_id`
- a `WorkingContext` carrying a source selection rejects persistent items whose source identity was not selected
- stale selected sources may remain visible as evidence, but their selection decision retains `authority_allowed=False`

## Separation

Resolution does not refresh sources, validate their factual correctness, authorize actions, or execute tools.

`WorkingContextComposer` remains responsible for assembling the final provider-neutral working context.

Task, execution state, execution progress, and observations remain separate working-context fields.

## Consequences

The M6.4 selection policy becomes an actual integration boundary instead of metadata-only guidance. Future memory, evidence, history, filesystem, web, or plugin-backed providers can implement source resolution behind the same contract without changing working-context semantics.
