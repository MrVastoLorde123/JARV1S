# Reasoning and Uncertainty Architecture

Phase 7 sits between world context and planning. It converts evidence-backed inputs into bounded interpretations and forecasts without promoting cognition into authority.

```text
Evidence + Provenance
        |
        v
World Snapshot / Current Context
        |
        v
Reasoning Context
        |
        +--> Evidence Signals
        |
        +--> Hypotheses
        |
        v
Belief Revision
        |
        +--> Support
        +--> Contradiction
        +--> Explicit Uncertainty
        |
        v
Advisory Predictions
        |
        v
Reasoning Trace / Evaluation
        |
        v
Planning / Initiative
```

## Epistemic separation

```text
Evidence ≠ Truth
Interpretation ≠ Truth
Hypothesis ≠ Fact
Belief ≠ Certainty
Prediction ≠ Permission
Confidence ≠ Certainty
Reasoning ≠ Authority
```

`ReasoningContext` identifies the world snapshot and supporting memory/context references used by a reasoning request. `EvidenceSignal` records explicit provenance, polarity, confidence, relevance, and a bounded likelihood ratio.

`BeliefRevision` uses deterministic `odds-v1` updating. The result is an inspectable belief score and uncertainty representation. It is not a truth-establishing mechanism and must not be treated as authorization.

`Prediction` carries an advisory forecast score, explicit uncertainty, time horizon, and assumptions. Prediction generation does not create plans, authorization, execution requests, notifications, or capability invocations.

`ReasoningTraceStep` preserves the reasoning path as structured metadata so downstream systems can inspect what context, evidence, revisions, and predictions were used.

## Provider boundary

Phase 7 deliberately does not call `ModelProviderBoundary`. A model suggestion can be admitted into cognition through a future bounded adapter, but the reasoning kernel itself remains deterministic and provider-neutral.

## Runtime boundary

`JarvisRuntime` may receive an optional `ReasoningSystem` dependency. Injection does not change the existing runtime authority properties. The runtime continues to expose no authorization, execution, truth, certainty, or provider-selection powers through the reasoning seam.
