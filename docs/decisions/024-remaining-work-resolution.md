# Decision 024 — Remaining-Work Resolution

## Status

Implemented — M5.4

## Context

M5.1 established deterministic assessment from verified `ExecutionState`. M5.2 added model-assisted interpretation, and M5.3 established a deterministic validation boundary preventing the model from contradicting observed execution reality.

The next problem is deciding what work actually remains after an execution attempt. `ExecutionAssessment.remaining` is useful semantic interpretation, but it cannot by itself become the source of future work because a model may introduce unrelated, unsupported, or speculative tasks.

At the same time, verified `ExecutionState.unresolved_requirements` must not be lost simply because the model summarized the situation differently.

## Decision

Introduce `RemainingWorkResolver` and the immutable `RemainingWork` value object.

The resolver receives both observed `ExecutionState` and an accepted `ExecutionAssessment` and deterministically produces a grounded representation of remaining work.

### Resolution rules

- the assessment goal must match the observed state goal;
- a completed execution resolves to no remaining work, regardless of model-supplied remaining items;
- every observed unresolved requirement is always preserved as remaining work;
- a model-supplied remaining item may be retained when it meaningfully matches an observed unresolved requirement;
- when no unresolved requirement text exists, a model-supplied remaining item may be retained only when it maps to an observed failed step;
- unrelated model-supplied remaining work is discarded;
- only model blocker descriptions that meaningfully correspond to observed requirements are retained;
- the resolver never executes, authorizes, confirms, repairs, or mutates execution state.

## Authority Model

```text
Observed ExecutionState
        |
        +----> deterministic assessment
        |
        +----> validated model assessment
                    |
                    v
          RemainingWorkResolver
                    |
                    v
             grounded work
                    |
                    v
          assessment-aware planning
```

Observed execution facts remain authoritative. Model reasoning can improve how remaining work is described, but cannot manufacture unsupported work or erase verified requirements.

## Safety Invariants

- observed unresolved requirements cannot disappear;
- completed execution cannot produce remaining work through model output;
- unrelated model work does not become a planning input merely because it was proposed;
- failed steps can ground corrective remaining work even when the executor did not emit a textual unresolved requirement;
- the resolver does not grant execution authority;
- downstream planning and execution remain subject to the existing validation, policy, confirmation, and executor boundaries.

## Consequence

M5.4 establishes a second deterministic epistemic boundary after assessment validation: **the work JARVIS plans to continue must be grounded in what the system actually observed**. This prepares M5.5 to plan against a stable remaining-work representation rather than directly trusting raw model interpretation.
