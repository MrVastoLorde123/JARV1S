# Decision 030: Working Context Consumption Boundary

## Status
Accepted for M6.6 implementation.

## Context

M6.1 through M6.5 established a provider-neutral `WorkingContext`, deterministic persistent-source selection, explicit source resolution, provenance checks, and safe admission of selected persistent context.

The remaining boundary is downstream consumption: how an already-composed `WorkingContext` reaches an AI provider without recreating context orchestration inside `JARVIS.ask()` or allowing downstream code to bypass source-selection rules.

## Decision

Introduce `WorkingContextConsumptionBoundary` as a narrow adapter:

```text
WorkingContext
     ↓
WorkingContextConsumptionBoundary
     ↓
AIRequest
     ↓
AIService
     ↓
AIProvider
```

The boundary accepts only a `WorkingContext` and converts it into the existing provider-neutral `AIRequest` contract.

`WorkingContext.to_context()` is the single provider-neutral representation consumed by the AI request. This preserves source-selection metadata, resolved context items, observations, conversation state, task state, and execution state/progress already carried by the working context.

## Responsibilities

The consumption boundary may:

- validate that its input is a `WorkingContext`;
- copy the working-context request into `AIRequest.task`;
- expose `WorkingContext.to_context()` as `AIRequest.context`;
- pass through model, generation options, and request metadata.

## Explicit non-responsibilities

The consumption boundary must not:

- retrieve memories, evidence, history, or external data;
- select or exclude context sources;
- refresh stale sources;
- validate epistemic truth;
- authorize actions;
- execute tools or plans;
- call an AI provider directly;
- mutate conversation or memory state;
- create a second request-orchestration pipeline.

## Why this boundary exists

The selector and resolver establish what persistent context is allowed to enter a `WorkingContext`. The consumer therefore accepts the **admitted object**, not raw context items or a second source-selection input. A downstream caller cannot use this seam to silently reintroduce excluded persistent sources.

`AIService` remains the existing provider dispatch owner. The consumption boundary is intentionally smaller than `JARVIS.ask()` and does not replace JARVIS orchestration.

## Invariant

> Reasoning may consume a `WorkingContext`, but reasoning consumption does not grant authority to retrieve, refresh, authorize, or execute.

## Consequence

M6.6 defines the safe handoff into reasoning. Actual request-lifecycle wiring in `JARVIS` should reuse this seam rather than adding another orchestration layer. Any future source acquisition or refresh flow must occur before consumption and must continue to enter through the established selection/resolution boundaries.
