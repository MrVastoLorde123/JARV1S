# Decision 031: Working Context Runtime Ownership

## Status

Proposed for M6.7 verification.

## Context

M6.1 through M6.6 established a provider-neutral `WorkingContext`, deterministic persistent-source selection, explicit source resolution, safe admission of selected persistent context, and a narrow consumption boundary that translates `WorkingContext` into `AIRequest`.

The remaining architectural gap is ownership of context construction. The existing conversation path still calls the legacy context builder directly, while the newer source-selection pipeline requires a bounded runtime entry point.

## Decision

Introduce `WorkingContextRuntime` as the single source-integrated context construction entry point.

```text
JARVIS request lifecycle
        |
        v
WorkingContextRuntime
        |
        +--> ContextSourceProvider
        |      |
        |      +--> available ContextSource values
        |      +--> corresponding ContextItem values
        |
        +--> ContextSourceIntegration
               |
               +--> ContextSourceSelector
               +--> ContextSourceResolver
               +--> WorkingContextComposer
        |
        v
WorkingContext
```

The runtime owns the coordination of context acquisition and construction. A `ContextSourceProvider` is the provider-neutral seam for obtaining already-available sources and their context items.

## Responsibilities

`WorkingContextRuntime` may:

- validate and normalize the request;
- ask the `ContextSourceProvider` for available persistent sources;
- ask the provider for corresponding context items;
- pass those inputs through the established selection/resolution/composition pipeline;
- carry explicit conversation, task, execution-state, progress, observation, metadata, and freshness-clock inputs into composition;
- return one `WorkingContext`.

## Explicit non-responsibilities

The runtime must not:

- call an AI service or provider;
- perform model reasoning;
- authorize actions;
- execute plans or tools;
- mutate conversation state;
- mutate memories or evidence;
- bypass `ContextSourceSelector` or `ContextSourceResolver`;
- directly construct an `AIRequest` for provider dispatch;
- become a second request-orchestration system.

## Ownership model

The boundaries are intentionally split:

- `JARVIS` owns the request lifecycle.
- `WorkingContextRuntime` owns context construction coordination.
- `ContextSourceProvider` owns source-specific acquisition mechanics behind a provider-neutral contract.
- `ContextSourceSelector` owns eligibility decisions.
- `ContextSourceResolver` owns resolution of selected identities to actual context items.
- `WorkingContextComposer` owns construction of the provider-neutral working context.
- `WorkingContextConsumptionBoundary` owns the handoff from working context to `AIRequest`.
- `AIService` owns provider dispatch.

No boundary above grants execution authority.

## Invariants

1. Persistent context reaches `WorkingContext` only through source selection and resolution.
2. The runtime cannot silently reintroduce excluded persistent sources.
3. Context construction does not require an AI call.
4. Context construction does not authorize or execute anything.
5. `JARVIS.ask()` remains the request-lifecycle owner.
6. M6.8 may replace the legacy direct `build_context()` path by calling this runtime without creating a second orchestration layer.

## Consequence

M6.7 establishes ownership without changing the live conversation request path. The legacy `build_context()` path remains untouched until M6.8 proves that `JARVIS.ask()` can consume `WorkingContextRuntime` and `WorkingContextConsumptionBoundary` while preserving existing behavior and regression coverage.
