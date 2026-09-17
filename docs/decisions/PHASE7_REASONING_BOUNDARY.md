# Decision — Phase 7 Reasoning Boundary

## Decision

Introduce a deterministic, provider-neutral reasoning subsystem between the Phase 6 world model and downstream planning/initiative layers.

## Why

JARVIS already has durable evidence, personal knowledge, current-world context, learning/adaptation, capabilities, security, and authority boundaries. The missing composition is an explicit cognitive boundary that can reason over those inputs without making its conclusions authoritative.

## Chosen semantics

- evidence signals carry polarity, confidence, relevance, likelihood-ratio input, and provenance;
- hypotheses are immutable candidate interpretations tied to a reasoning context;
- belief revision is explicit and deterministic (`odds-v1`);
- conflicting support is preserved as `CONFLICTED` rather than silently collapsed;
- predictions are advisory forecasts with explicit uncertainty and time horizons;
- reasoning traces make cognitive transformations inspectable;
- runtime integration is dependency injection only.

## Rejected shortcuts

### Model output as truth
Rejected because provider/model output remains a suggestion and can be wrong, stale, incomplete, or conflicting with other evidence.

### Highest confidence as truth
Rejected because confidence is uncertainty metadata, not a truth oracle.

### Prediction as permission
Rejected because a forecast describes a possible future and cannot authorize an action.

### Automatic persistence
Rejected because reasoning results should cross the existing memory/learning boundaries explicitly rather than silently mutating durable state.

## Boundary invariant

```text
More reasoning capability
+ more evidence
+ better prediction
        !=
more authority
```
