# Decision 032: Live Working Context Migration

## Status
Implemented for M6.8 migration; verification pending.

## Context

M6.1 through M6.7 established the provider-neutral `WorkingContext`, deterministic persistent-source selection, explicit source resolution, safe admission, a provider-neutral consumption boundary, and a dedicated runtime that owns context construction.

The legacy conversation path in `JARVIS._handle_conversation()` previously called `build_context()` directly and constructed `AIRequest` itself. That bypassed the new working-context runtime and consumption seams.

## Decision

M6.8 migrates only the conversation context segment of `JARVIS`:

```text
Before:
JARVIS.ask()
  -> build_context()
  -> AIRequest
  -> AIService

After:
JARVIS.ask()
  -> WorkingContextRuntime.compose()
  -> WorkingContextConsumptionBoundary.consume()
  -> AIRequest
  -> AIService
```

`JARVIS.ask()` remains the request lifecycle owner. Routing, conversation persistence, memory formation, response construction, task execution, policy, and confirmation remain in their existing JARVIS-owned paths.

## Runtime composition

The default context runtime uses a memory-backed `ContextSourceProvider` that adapts the existing deterministic memory retrieval into `ContextSource` and `ContextItem` values. The resulting sources still pass through `ContextSourceIntegration`, which owns selector, resolver, and composer sequencing.

`ContextOptions` continue to control whether memories and evidence participate and their existing limits are passed into the default memory source provider.

## Responsibilities

`JARVIS`:
- owns the overall request lifecycle;
- records user and assistant conversation turns;
- invokes the context runtime for conversation requests;
- passes the consumed `AIRequest` to `AIService`;
- performs existing persistence and memory-formation behavior.

`WorkingContextRuntime`:
- acquires available persistent context through `ContextSourceProvider`;
- routes acquisition through source selection, resolution, and composition;
- receives explicit conversation/task/execution/observation state;
- returns a `WorkingContext`.

`WorkingContextConsumptionBoundary`:
- converts the admitted `WorkingContext` into `AIRequest`;
- performs no retrieval, selection, authorization, or execution.

## Explicit non-changes

M6.8 does not redesign:
- request routing;
- command handling;
- task planning or execution;
- confirmation policy;
- conversation persistence;
- memory formation;
- AI provider dispatch.

## Invariant

> The live conversation path consumes the context architecture without making `JARVIS.ask()` a context engine and without creating a second request orchestrator.
