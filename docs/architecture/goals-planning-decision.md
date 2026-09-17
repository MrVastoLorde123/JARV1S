# Goals, Planning, and Decision Support

JARVIS planning is a bounded cognitive layer between reasoning and downstream initiative/authority.

```text
Evidence + World Context
          ↓
Reasoning / Uncertainty / Prediction
          ↓
Goals / Objectives
          ↓
Planning Context
          ↓
Candidate Plans
          ↓
Feasibility + Utility Evaluation
          ↓
Deterministic Advisory Ranking
          ↓
Advisory Plan Selection
          ↓
Initiative / Validation / Policy / Confirmation / Authorization
          ↓
Execution
```

## Goal

A goal records a desired outcome, priority, lifecycle state, temporal horizon, and constraints. A goal expresses direction; it is not an instruction to act.

## Planning context

A planning context binds one goal to the current world snapshot and reasoning result. This prevents planning from silently consuming stale or unrelated state.

## Candidate plans

Candidate plans contain descriptive steps, dependencies, assumptions, expected benefit, effort, risk, and confidence. Steps are intentionally provider-neutral and contain no callable execution surface.

## Evaluation and ranking

Feasibility states are explicit:

- `FEASIBLE` — structurally usable for advisory comparison.
- `REVIEW` — current world/reasoning ambiguity requires human or downstream review.
- `BLOCKED` — unresolved blocker or inactive goal prevents advisory selection.

Ranking is deterministic: feasible candidates outrank review candidates, review candidates outrank blocked candidates, then advisory score descends and plan identity provides the deterministic tie-break.

The advisory score is bounded to `[0,1]` and combines expected benefit, confidence, effort, and risk. It does not represent a probability of success and cannot grant permission.

## Authority separation

```text
Plan Selection ≠ Authorization
Plan ≠ Execution
Utility ≠ Permission
Feasibility ≠ Permission
```

The planning system has no provider selection, tool invocation, persistence, external mutation, authorization, or execution surface.
