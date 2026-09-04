# M15.3 — Initiative Evaluation

## Purpose

Evaluate an `InitiativeCandidate` using explicit bounded criteria before any later proposal or action stage.

## Boundary

Evaluation is descriptive judgment. It is not:

- authorization
- policy
- confirmation
- instruction
- execution request
- obligation
- truth guarantee

## Criteria

Each evaluation records normalized scores from `0.0` to `1.0` for:

- value
- urgency
- confidence
- effort
- risk

A deterministic `net_signal` summarizes those criteria for comparison. It does not grant permission or determine execution.

## Flow

```text
World Model
  ↓
Detection
  ↓
Initiative Candidate
  ↓
Initiative Evaluation
  ↓
M15.4 Proposal
  ↓
Existing Validation / Policy / Confirmation / Authorization
```

## Safety walls

- Evaluation ≠ Authorization
- Score ≠ Permission
- Confidence ≠ Certainty
- Value ≠ Obligation
- Urgency ≠ Authority
- Risk ≠ Policy Decision
- Evaluation ≠ Execution
