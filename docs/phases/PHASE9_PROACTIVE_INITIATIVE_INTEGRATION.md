# Phase 9 — Proactive Initiative Integration

## Purpose

Bridge the verified Phase 8 planning boundary into the existing proactive-initiative stack without rebuilding or widening authority.

## Milestones

- **M118 — Planning-to-Initiative Detection Bridge**
  Convert plan evaluations into bounded descriptive opportunity/gap/change detections.
- **M119 — Goal / Plan / World / Reasoning Lineage**
  Preserve planning context, world snapshot, reasoning result, goal, and plan identity through initiative artifacts.
- **M120 — Value / Effort / Risk / Confidence Projection**
  Project candidate-plan utility factors into the existing initiative evaluation contract.
- **M121 — Initiative Candidate Formation**
  Form an immutable initiative candidate only from a feasible advisory plan.
- **M122 — Proactive Proposal Formation**
  Translate the selected feasible plan into the existing proposal artifact while preserving confirmation requirements.
- **M123 — Scheduling Recommendation Integration**
  Optionally construct a schedule proposal; never create a scheduler entry or deliver a notification.
- **M124 — Initiative Safety Boundary**
  Reuse the existing safety contract to keep proposal artifacts below confirmation, authorization, policy, and execution.
- **M125 — Proactive Composition / Review States**
  Produce one inspectable result that preserves blocked/review/no-selection states and selected-proposal lineage.
- **M126 — Runtime Integration Boundary**
  Inject the proactive initiative system into the runtime kernel without granting execution authority.

## Boundary

```text
Planning Result
      ↓
Initiative Detection
      ↓
Initiative Candidate
      ↓
Initiative Evaluation
      ↓
Proactive Proposal
      ↓
Scheduling Recommendation (optional)
      ↓
Safety Boundary
      ↓
Downstream Validation / Confirmation / Authorization
```

The subsystem does **not** authorize, execute, schedule delivery, send notifications, select providers, invoke tools, mutate policy, establish truth, or establish certainty.

## Design rules

1. A blocked plan never becomes a proposal.
2. Ambiguous world/reasoning state remains a review state and does not create an advisory selection.
3. A planning selection is not authorization.
4. A schedule artifact is not a scheduled runtime job.
5. Existing initiative artifacts remain the canonical proposal/scheduling/safety representation.
6. Planning, initiative, and authority remain separate layers.
