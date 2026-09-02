# Decision 026 — Persistent Working Context

## Status

Accepted for M6.1.

## Decision

JARVIS will represent its current working situation through a provider-neutral `WorkingContext` contract.

`WorkingContext` composes existing context data without replacing the source-specific contracts already established in the system.

```text
ContextPackage
    + Conversation State
    + Current Task
    + Execution State
    + Execution Progress
    + Observations
            ↓
      WorkingContext
            ↓
 downstream reasoning / orchestration
```

The existing `ContextPackage` remains responsible for context-builder concerns such as memories, evidence, history, and state-derived context items. `WorkingContext` is a composition boundary around that package rather than a replacement for it.

## Composition Boundary

`WorkingContextComposer` is responsible only for composition and normalization.

It may:

- invoke the existing context builder
- attach an immutable conversation snapshot
- attach the current `TaskRequest`
- attach verified `ExecutionState`
- attach cumulative `ExecutionProgress`
- normalize explicit observations into provider-neutral `ContextItem` values
- expose a provider-neutral `to_context()` representation

It must not:

- call an AI provider
- execute tools or tasks
- authorize actions
- validate execution plans
- mutate memory
- mutate conversation state
- infer facts that were not supplied by a source

## Authority

Working context is informational. It does not grant authority.

In particular:

- conversation context does not authorize execution
- task context does not authorize execution
- execution state remains the authoritative observation of execution
- execution progress remains historical execution evidence
- observations are supplied evidence, not automatically verified facts

The existing execution safety chain remains authoritative:

`validation → policy → confirmation (when required) → executor → capability`

## Goal Consistency

When both `ExecutionState` and `ExecutionProgress` are supplied, they must belong to the same goal. This prevents the composer from silently combining execution evidence from unrelated tasks.

## Provider Neutrality

`WorkingContext` contains no AI-provider-specific types or behavior. Downstream model adapters may consume `to_context()`, but model-specific formatting remains outside the context composition layer.

## Consequence

M6 now has a stable seam for combining the user's present request with relevant persistent and execution context.

Future M6 work can extend the sources feeding this contract without turning `JARVIS` into a context-specific dependency hub.
