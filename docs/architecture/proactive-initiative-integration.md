# Proactive Initiative Integration Architecture

Phase 9 connects the verified planning layer to the existing M15/M21 proactive initiative artifacts.

```text
World Model + Reasoning
          ↓
       Planning
          ↓
  Plan Evaluation / Ranking
          ↓
  Initiative Detection
          ↓
  Initiative Candidate
          ↓
  Initiative Evaluation
          ↓
  Initiative Proposal
          ↓
  Schedule Recommendation
          ↓
  Initiative Safety
          ↓
Validation → Policy → Confirmation → Authorization → Execution
```

## Reused canonical artifacts

- `OpportunityDetectionSet`
- `InitiativeCandidate`
- `InitiativeEvaluation`
- `InitiativeProposal`
- `ProactiveSchedule`
- `InitiativeSafetyResult`
- `InitiativeRuntime`

Phase 9 does not replace these artifacts. The new `ProactiveInitiativeSystem` is an integration boundary around them.

## Semantic walls

```text
Plan Selection ≠ Initiative Instruction
Initiative ≠ User Intent
Evaluation ≠ Approval
Proposal ≠ Confirmation
Schedule Recommendation ≠ Scheduling
Schedule ≠ Authorization
Safety ≠ Authorization
Authorization ≠ Execution
```

## Review behavior

A blocked plan produces a descriptive gap detection and no proposal. An ambiguous world or reasoning result produces a review/change detection and no advisory selection. Only a feasible advisory selection can cross into the proposal-only initiative artifacts.

The runtime receives the proactive system as a dependency seam only. It does not invoke it automatically and does not expand runtime authority.
