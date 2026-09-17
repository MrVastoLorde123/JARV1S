# Phase 8 — Goals, Planning, and Decision Support

## Objective

Bridge bounded reasoning into structured goal-directed planning without turning a selected plan into authority or execution.

## Milestones

- M109 — Goal Contract
- M110 — Planning Context Contract
- M111 — Candidate Plan / Step Model
- M112 — Feasibility and Constraint Evaluation
- M113 — Benefit / Effort / Risk / Confidence Model
- M114 — Deterministic Plan Ranking
- M115 — Advisory Plan Selection Result
- M116 — Planning Decision System Composition
- M117 — Runtime Integration Boundary

## Architecture

```text
World Snapshot + Reasoning Result
              |
              v
       Planning Context
              |
              v
        Goal / Objective
              |
              v
       Candidate Plans
              |
       +------+------+
       |             |
  Feasibility   Utility Signals
       |             |
       +------+------+
              |
              v
    Deterministic Ranking
              |
              v
     Advisory Plan Selection
              |
              v
       Initiative / Proposal / Authority
```

## Boundary

Planning describes what could be done to pursue a goal. It does not make execution authoritative.

```text
Goal ≠ Authorization
Plan ≠ Execution
Plan Selection ≠ Authorization
Feasibility ≠ Permission
Utility ≠ Permission
Confidence ≠ Certainty
Reasoning ≠ Planning
Planning ≠ Execution
```

Ambiguous world or reasoning state produces `REVIEW` rather than silently becoming a confident plan. Blocked candidates remain visible but cannot outrank feasible candidates.

The current ranking formula is deterministic and bounded. It is an advisory comparison signal only.

## Verification gate

Phase closure requires one consolidated local receipt containing the focused Phase 8 suite, the Phase 8 structural verifier, the UI production build, and the full core regression suite. A remote implementation alone does not close the phase.
