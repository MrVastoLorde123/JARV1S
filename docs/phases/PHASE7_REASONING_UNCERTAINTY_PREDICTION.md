# Phase 7 — Reasoning, Uncertainty, and Prediction

## Objective

Establish a provider-neutral reasoning layer that consumes provenance-backed evidence and the immutable world-model context from Phase 6 and produces inspectable hypotheses, bounded belief revisions, advisory predictions, and deterministic reasoning traces.

## Milestones

- M100 — Canonical Reasoning Context Contract
- M101 — Evidence Signal and Weighting Contract
- M102 — Hypothesis Representation
- M103 — Belief Revision
- M104 — Conflict and Uncertainty Representation
- M105 — Bounded Prediction Contract
- M106 — Reasoning Trace and Evaluation
- M107 — Reasoning System Composition Boundary
- M108 — Runtime Integration Boundary

## Architecture

```text
Persistent Intelligence / Provenance
                  |
                  v
       Phase 6 World Snapshot
                  |
                  v
          Reasoning Context
                  |
         +--------+--------+
         |                 |
         v                 v
    Evidence Signals    Hypotheses
         |                 |
         +--------+--------+
                  v
          Belief Revision
                  |
         +--------+--------+
         |                 |
         v                 v
     Conflicts         Predictions
         |                 |
         +--------+--------+
                  v
        Reasoning Trace
                  |
                  v
        Evaluation / Context
                  |
                  v
             Planning
```

## Epistemic rules

Reasoning is interpretation over evidence. A belief revision is not a truth claim. A prediction is an advisory forecast; its score is not calibrated certainty and cannot become permission. Conflicting evidence remains explicit instead of being erased by a single selected answer.

The initial revision method is `odds-v1`: explicit prior belief plus bounded evidence likelihood-ratio contributions. This is a transparent deterministic update mechanism, not a claim that the resulting score is objectively calibrated probability.

## Non-authority rules

The reasoning subsystem:

- does not establish truth;
- does not establish certainty;
- does not grant permission or authorization;
- does not execute capabilities;
- does not select providers;
- does not invoke tools or external processes;
- does not persist durable state;
- does not mutate external state.

Model output may later feed `EvidenceSignal` or proposal-generation paths, but a model remains a replaceable suggestion source rather than JARVIS authority.

## Verification gate

Phase closure requires one consolidated local receipt containing:

1. focused Phase 7 suite;
2. Phase 7 structural verifier;
3. UI production build;
4. full core regression.

Remote implementation is not sufficient to close the phase.
