# Decision 022 — Model-Assisted Execution Assessment

## Status
Accepted — M5.2

## Context
M5.1 introduced deterministic `ExecutionAssessment` as a trusted interpretation of verified `ExecutionState`. The next step is to let a model reason semantically about what that state means and what work remains without allowing model output to redefine observed execution facts.

## Decision
Introduce `ModelExecutionAssessmentService` as a provider-neutral reasoning boundary.

The service:

- receives verified `ExecutionState`;
- derives the deterministic baseline assessment first;
- provides both state and baseline assessment to the AI provider;
- accepts a structured model interpretation of situation, completed work, remaining work, blockers, recommendation, and confidence;
- preserves `useful_outputs` from the deterministic assessment rather than accepting model-supplied outputs;
- returns an `ExecutionAssessment` only and never validates, authorizes, confirms, executes, or invokes capabilities.

The model therefore acts as an interpreter of verified state, not as the source of execution truth.

## Safety invariants

- Observed execution state remains authoritative.
- Model output cannot directly execute or authorize an action.
- Verified outputs are never replaced by model-invented outputs.
- Structured parsing rejects malformed or out-of-range model output.
- The existing validator -> policy -> confirmation -> executor pipeline remains downstream of any later plan generated from an assessment.

## Consequence
JARVIS now has a distinct reasoning boundary between deterministic observation and future assessment-aware planning. M5.3 can therefore focus on validating model interpretation against observed reality before any assessment is allowed to influence planning.
