# Phase 2 — Experience, Learning & Adaptation

## Objective

Turn verified agency outcomes into structured experience, derive bounded learning,
propose and validate adaptations, apply validated learning as an immutable profile
transition, and measure the adaptation outcome.

## Milestones

- M60 — Outcome / Experience Feedback
- M61 — Experience Record
- M62 — Learning Signal
- M63 — Learning Evaluation
- M64 — Adaptation Proposal
- M65 — Adaptation Validation
- M66 — Adaptation Application
- M67 — Adaptation Outcome

## Architectural invariant

Experience is evidence about what happened. Learning is a bounded interpretation of
experience. Adaptation is a proposal derived from evaluated learning. Validation
must precede application. Application changes only the immutable learning profile
model; it does not mutate authority, tools, credentials, execution state, or policy.

## Closed loop

```text
M59 Reconciliation
    ↓
M60 Experience Feedback
    ↓
M61 Experience Record
    ↓
M62 Learning Signal
    ↓
M63 Learning Evaluation
    ↓
M64 Adaptation Proposal
    ↓
M65 Adaptation Validation
    ↓
M66 Adaptation Application
    ↓
M67 Adaptation Outcome
    ↓
future experience feedback
```

## Non-responsibilities

Phase 2 does not create authorization, perform execution, select providers/tools,
perform independent verification, persist externally, or grant itself authority.

## Completion gate

The phase requires the focused Phase 2 test suite, the consolidated static contract
verifier, the UI production build, and the full `src.core.tests` regression baseline.
