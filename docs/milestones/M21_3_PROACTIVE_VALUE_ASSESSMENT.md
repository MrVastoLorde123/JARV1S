# M21.3 — Proactive Value Assessment

## Purpose

M21.2 establishes that an eligible initiative may become a bounded proactive proposal. M21.3 adds a deterministic advisory estimate of the proposal's relative value so later prioritization can compare proposals without turning value into authority.

## Flow

```text
Initiative Candidate
        ↓
Initiative Evaluation
        ↓
Proactive Proposal
        ↓
Value Factors
        ↓
Value Assessment
        ↓
[future prioritization layer]
```

M21.3 stops at value assessment. It does not schedule, select for execution, authorize, or execute a proposal.

## Value factors

Each factor is normalized to `[0, 1]`:

- `importance`
- `urgency`
- `expected_benefit`
- `confidence`
- `effort_cost`
- `risk`

The model is deliberately explicit. Confidence is evidential strength, not certainty. Effort and risk are costs to the advisory score, not policy decisions.

## Deterministic scoring

```text
score =
    0.25 * importance
  + 0.20 * urgency
  + 0.25 * expected_benefit
  + 0.10 * confidence
  - 0.10 * effort_cost
  - 0.10 * risk
```

The result is clamped to `[0, 1]`.

The formula is versioned as `linear-v1` so future changes cannot silently reinterpret historical assessments.

## Deterministic ranking

Advisory ranking sorts by:

1. score descending
2. proposal identity ascending as the deterministic tie-breaker

Ranking is informational only.

## Authority walls

```text
Value ≠ Truth
Score ≠ Certainty
Value ≠ User Intent
Ranking ≠ Selection Authority
Ranking ≠ Scheduling
Ranking ≠ Authorization
Proposal Value ≠ Permission
Prioritization ≠ Execution
```

## Non-goals

M21.3 does not:

- create tasks
- schedule work
- notify the user
- authorize proposals
- execute capabilities
- modify policy
- change permissions
- infer that a high score means a proposal is correct

## Test target

Focused tests cover deterministic scoring, bounds, immutable value factors, authority exclusion, context isolation, deterministic ranking, and mapping identity validation.
