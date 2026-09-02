# Decision 023 — Execution Assessment Validation

## Status

Accepted — M5.3

## Context

M5.1 established deterministic `ExecutionAssessment` from observed `ExecutionState`. M5.2 added model-assisted interpretation, but structured model output can still be internally valid while contradicting observed execution reality.

For example, the model may report:

```text
completed: ["modify authentication config"]
```

while the observed state records:

```text
failed_steps: ("modify",)
```

A syntactically valid model response is therefore not sufficient evidence of a valid assessment.

## Decision

Introduce `ExecutionAssessmentValidator` as the deterministic epistemic boundary between model interpretation and downstream planning.

The validator receives both the observed `ExecutionState` and the proposed `ExecutionAssessment` and rejects interpretations that contradict authoritative execution facts.

### Validation rules

- assessment goal must match the observed goal;
- a non-completed execution may not be described as `objective_completed`;
- a completed execution must be described as `objective_completed`;
- every model `completed` claim must resolve to an observed completed step;
- a model `completed` claim that resolves to an observed failed step is rejected;
- observed unresolved requirements cannot disappear from the model's blocker interpretation.

Semantic step matching is deterministic and conservative: a claim may elaborate an observed step, but it cannot introduce an unrelated completed action.

## Authority Model

The observed execution state remains authoritative.

```text
Observed ExecutionState
        |
        +----> deterministic assessment
        |
        +----> model interpretation
                    |
                    v
          Assessment Validator
                    |
             valid / reject
                    |
                    v
          assessment-aware planning
```

The validator does not execute, authorize, confirm, or repair anything. Rejection means the model's interpretation cannot be trusted for downstream planning; the caller must retain the observed state or obtain a new interpretation.

## Safety Invariants

- Model confidence never overrides deterministic validation.
- A model cannot turn a failed step into completed work.
- A model cannot manufacture completed work that was never observed.
- Observed blockers remain represented in an accepted assessment.
- Validation occurs before an assessment can influence future planning.
- This boundary does not replace the existing plan validation, policy, confirmation, or execution boundaries.

## Consequence

M5.3 establishes the first explicit epistemic boundary for JARVIS: **model interpretation is evidence, not truth**. The model can reason about what happened, but deterministic observation decides whether that interpretation is admissible.
