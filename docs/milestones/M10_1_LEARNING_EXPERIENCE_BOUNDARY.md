# M10.1 — Learning / Experience Boundary

## Status

**IMPLEMENTED — awaiting user verification**

M10.1 establishes the foundation for intelligence and learning by defining what an experience is before defining how JARVIS learns from it.

## Core idea

> JARVIS does not just accumulate memories. It accumulates lessons.

M10.1 deliberately stops before lesson extraction or behavioral adaptation. Experiences are immutable evidence that later M10 stages may evaluate.

## Experience model

```text
Experience
├── experience_id
├── source
├── objective_id
├── action_reference
├── decision_reference
├── observations
├── outcome
├── user_feedback
├── evaluation
├── confidence
└── provenance
```

## Semantic walls

```text
Experience ≠ Truth
Experience ≠ Policy
Experience ≠ Authorization
Experience ≠ User Intent

Learning ≠ Authority
Confidence ≠ Certainty
Experience ≠ Execution
```

## Architecture

```text
Memory / Observation / Outcome
              ↓
          Experience
              ↓
         [M10.1 boundary]
              ↓
       Future evaluation
              ↓
        Future learning
              ↓
     Better reasoning / behavior
              ↓
           M7 Authority
```

## Implementation

`src/learning/experience.py` provides:

- immutable `Experience`
- explicit event references and provenance
- bounded confidence semantics
- provider-neutral serialization
- explicit non-authoritative serialization flags
- immutable conflict-aware `ExperienceStore`

`src/learning/tests/test_experience.py` provides focused contract coverage.

## Non-goals

M10.1 does not perform model training, lesson extraction, behavioral adaptation, policy mutation, authorization, execution, or autonomous self-modification.

## Verification target

Focused:

```text
python -m unittest src.learning.tests.test_experience -v
```

Full suite:

```text
python -m unittest
```
