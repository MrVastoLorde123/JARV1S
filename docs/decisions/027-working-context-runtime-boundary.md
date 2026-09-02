# Decision 027 — Working Context Runtime Boundary

## Status

Accepted for M6.2.

## Decision

JARVIS runtime state is exposed to the working-context system through `JARVISWorkingContextRuntime`.

The runtime boundary:

```text
JARVIS instance
    ↓
JARVISWorkingContextRuntime
    ↓
WorkingContextComposer
    ↓
WorkingContext
```

`JARVISWorkingContextRuntime` reads the current conversation state and context options from the JARVIS instance and delegates composition to the existing `WorkingContextComposer`.

## Responsibilities

The runtime boundary may:

- read the current conversation snapshot
- read configured context options
- attach an explicit task
- attach verified execution state and progress
- attach explicit observations and supplied history
- delegate to `WorkingContextComposer`

It must not:

- call an AI provider
- execute tasks or tools
- authorize actions
- mutate conversation state
- mutate memories
- replace `WorkingContextComposer` composition rules

## Separation

`JARVIS` remains the orchestration owner.

`WorkingContextComposer` remains responsible for composition and normalization.

`JARVISWorkingContextRuntime` is only the integration seam between the two.

This prevents working-context construction from becoming another responsibility embedded throughout `JARVIS.ask()` and keeps the context subsystem independently testable.

## Consequence

Future runtime flows can request one coherent `WorkingContext` from the current JARVIS state without introducing context-specific dependencies throughout core orchestration.

The next M6 work can focus on improving which persistent sources are selected and when they are refreshed, without changing the runtime boundary.
