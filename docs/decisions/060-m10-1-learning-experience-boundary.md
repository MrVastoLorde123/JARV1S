# Decision 060 — M10.1 Learning / Experience Boundary

## Status

**ACCEPTED**

## Context

M9 established bounded workforce, recovery, and objective continuation while preserving the M7 authority chain. M10 introduces intelligence and learning. Before JARVIS can improve its behavior, the system needs a precise boundary for what constitutes an experience that may later become learning evidence.

## Decision

M10.1 defines an immutable `Experience` as a provider-neutral record describing a bounded event around an objective, action or decision, observations, outcome, user feedback, evaluation, confidence, and provenance.

Experience records are evidence for later evaluation and learning. They do not themselves change behavior, policy, authorization, permission, execution state, or user intent.

An immutable `ExperienceStore` may retain records and reject conflicting identities, but it does not infer lessons, change policy, or authorize action.

## Experience contract

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
Experience ≠ Execution
Confidence ≠ Certainty
```

## Required properties

- Identity is explicit and stable through `experience_id`.
- Experience is immutable after creation.
- Observation references are explicit, unique, and bounded by the record itself.
- Confidence, when supplied, is constrained to `[0.0, 1.0]` and is not certainty.
- Provenance is retained for later inspection and attribution.
- Serialization exposes the evidence while explicitly denying truth, policy authority, authorization, and execution semantics.
- Duplicate experience identities are explicit conflicts, not silent overwrites.

## Consequences

M10 can now build later stages on a stable evidence boundary:

```text
Observation / Outcome
        ↓
Experience
        ↓
Evaluation
        ↓
Learning Candidate
        ↓
Validated Lesson / Adaptation
```

Only the later validation and adaptation stages may determine whether an experience should change behavior. Any resulting executable behavior must still re-enter the established M7/M8/M9 authority boundaries.

## Non-goals

M10.1 does not implement:

- model training or fine-tuning
- automatic policy mutation
- automatic authorization
- behavioral self-modification
- autonomous execution
- unbounded learning loops
- truth inference from a single experience
