# Decision 064 — M10.5 Reasoning Quality Feedback Loop

## Status

IMPLEMENTATION IN PROGRESS

## Decision

M10.5 introduces a provider-neutral, immutable reasoning-quality feedback boundary. The boundary evaluates explicit quality signals about a reasoning trace and converts them into bounded feedback signals that may inform future learning or adaptation, but cannot itself authorize, execute, mutate policy, expand capabilities, or establish truth.

## Boundary

```text
Reasoning / Decision
      ↓
Observed Outcome
      ↓
Evidence + Evaluation
      ↓
Reasoning Quality Assessment
      ↓
Feedback Signal
      ↓
Explicit Learning / Adaptation Boundary
      ↓
Future Reasoning Context
```

## Quality model

M10.5 currently evaluates five bounded dimensions:

- OUTCOME_ALIGNMENT
- EVIDENCE_USE
- CLARITY
- CONSISTENCY
- EFFICIENCY

Each dimension uses an explicit score in `[0.0, 1.0]` and requires a rationale. Overall quality is the deterministic arithmetic mean of supplied dimensions. Duplicate dimensions are rejected.

## Feedback model

Feedback is derived deterministically from the overall score:

- `>= 0.8` → RETAIN
- `>= 0.6` → IMPROVE
- `>= 0.4` → CAUTION
- `< 0.4` → INSUFFICIENT

These signals describe learning guidance only. They are not permissions or policy mutations.

## Provenance

Assessments may reference the M10.2 evaluation that motivated them. Feedback preserves its originating assessment identity. Stores reject conflicting identities and preserve immutable history.

## Semantic walls

```text
Reasoning Evaluation ≠ Truth
Feedback ≠ Authority
Quality Signal ≠ Permission
Learning ≠ Authorization
Prediction ≠ Certainty
Self-Evaluation ≠ Self-Authority
Reasoning Improvement ≠ Authority Expansion
Memory ≠ User Intent
```

## Non-goals

M10.5 does not:

- grant authority or authorization
- invoke execution or plugins
- expand capabilities
- silently mutate policy
- claim fabricated success or failure
- treat model confidence as correctness
- autonomously modify reasoning policy

## Relationship to M10.3

M10.5 feedback may be consumed by the explicit M10.3 adaptation boundary later. M10.5 does not call or mutate `AdaptationController`; any behavioral change remains subject to the existing explicit acceptance boundary.

## Relationship to M10.4

Reasoning-quality feedback is not automatically consolidated into durable memory. Any memory formation must continue through M10.4's explicit consolidation boundary.
