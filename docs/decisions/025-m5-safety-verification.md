# Decision 025 — M5 Safety Verification

## Status

Implemented — M5.6 pending user verification

## Context

M5 introduced a chain that lets JARVIS interpret verified execution state, use model-assisted reasoning, validate that interpretation against observed reality, resolve grounded remaining work, and plan from that grounded state.

The chain must not become a second execution authority or allow model reasoning to bypass existing validation, policy, confirmation, or execution controls.

## Decision

M5.6 is a verification milestone rather than a new autonomous feature.

The safety suite verifies that:

- observed failed work remains failed when model confidence is high;
- completed claims remain grounded in observed completed steps;
- verified execution outputs cannot be replaced by model-supplied outputs;
- invalid assessments are rejected before planning;
- completed execution remains distinguishable from partial or blocked interpretation;
- grounded remaining work is explicitly supplied to assessment-aware planners;
- assessment-aware plans still pass through deterministic execution policy;
- assessment and execution state remain immutable/provider-neutral boundaries.

## Authority Model

```text
Observed ExecutionState
        ↓
Deterministic Assessment
        ↓
Model Interpretation
        ↓
Assessment Validation
        ↓
Remaining-Work Resolution
        ↓
Assessment-Aware Planning
        ↓
Plan Validation → Policy → Confirmation → Executor
```

No M5 component grants execution authority to a model or assessment.

## Consequence

A passing M5.6 suite establishes that the complete assessment-to-planning path preserves the project's structural safety boundaries. M5 is complete only after the full regression suite passes with the M5.6 tests included.
