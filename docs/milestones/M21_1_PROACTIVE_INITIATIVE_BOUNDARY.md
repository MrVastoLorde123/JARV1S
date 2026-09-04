# M21.1 — Proactive Initiative Boundary

## Purpose

M20 established bounded long-horizon continuation for work already represented as a goal, objective, and task graph. M21 introduces the ability for JARVIS to notice that something may deserve attention without turning that notice into autonomous action.

M21.1 therefore defines the boundary between a **signal** and a future **initiative candidate**.

## Flow

```text
Signal / Observation
        ↓
ProactiveTrigger
        ↓
InitiativeCandidate
        ↓
InitiativeEvaluation
        ↓
[future M21 proposal layer]
```

The M21.1 implementation stops at evaluation.

## Core contracts

### `ProactiveTrigger`

An immutable record of a signal observed by the system.

A trigger preserves:
- source category
- source/reference identity
- signal description
- observation timestamp
- optional evidence identities
- non-authoritative metadata

A trigger is **not** user intent, truth, authorization, or an execution request.

### `InitiativeCandidate`

An immutable bounded candidate that says, in effect, **“this may deserve consideration.”**

It preserves:
- candidate identity
- originating trigger identity
- human-readable title and rationale
- evidence identities
- optional expiry

It cannot grant authorization or request execution.

### `InitiativeEvaluation`

An immutable deterministic disposition:

- `ELIGIBLE`
- `NEEDS_REVIEW`
- `SUPPRESSED`
- `EXPIRED`

Evaluation controls whether the candidate can proceed to a later proposal-stage decision. It does not perform that decision itself.

## Authority walls

```text
Trigger ≠ User Intent
Initiative Candidate ≠ Proposal
Initiative Candidate ≠ Authorization
Proactive Evaluation ≠ Permission
Signal ≠ Truth
Eligibility ≠ Action
Proactivity ≠ Autonomous Agency
```

## Deterministic rules

1. Candidate and trigger identities must match.
2. Explicit suppression wins before other dispositions.
3. Expiry is evaluated at a supplied, timezone-aware evaluation time.
4. Review requests produce `NEEDS_REVIEW` and do not bypass the boundary.
5. Otherwise the candidate is `ELIGIBLE` for a later proposal-stage decision.
6. No function in M21.1 creates tasks, schedules work, notifies the user, grants authorization, or executes anything.

## Test receipt

Focused M21.1 tests cover immutability, metadata isolation, identity binding, expiry, suppression precedence, review handling, and authority/execution absence.

Verification is considered complete only after the local focused test suite and full core regression are green.
