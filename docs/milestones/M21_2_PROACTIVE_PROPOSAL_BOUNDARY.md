# M21.2 — Proactive Proposal Boundary

## Purpose

M21.1 established that JARVIS may detect a bounded initiative candidate without treating a signal as intent or action. M21.2 introduces the next cognitive boundary: an eligible initiative may be formulated as a proposal for later validation.

The proposal is a recommendation. It is not a task, schedule, permission, authorization, or execution request.

## Flow

```text
Signal / Observation
        ↓
Evidence + Provenance
        ↓
Initiative Candidate
        ↓
Initiative Evaluation
        ↓
Initiative Proposal
        ↓
[future validation / prioritization]
```

## Core contract

### `InitiativeProposal`

An immutable recommendation derived from one eligible `InitiativeCandidate`.

It preserves:
- proposal identity
- originating candidate and trigger identities
- recommendation text
- candidate rationale
- evidence identities
- optional creation and expiry timestamps
- optional bounded confidence value

Confidence represents uncertainty about the recommendation. It is not certainty, truth, permission, or authority.

### `ProposalEvaluation`

An immutable result containing either:
- `PROPOSED` with one bounded proposal, or
- `NEEDS_REVIEW` with no proposal.

Only an `ELIGIBLE` initiative disposition may form a proposal. Suppressed, expired, or review-bound candidates remain outside proposal formation.

## Deterministic rules

1. Candidate and evaluation identities must match.
2. Only `ELIGIBLE` candidates may produce a proposal.
3. Candidate evidence identities are preserved into the proposal.
4. Proposal timestamps must be timezone-aware.
5. Proposal expiry cannot precede proposal creation.
6. Confidence, when present, is bounded to `[0, 1]`.
7. A proposal is immutable and permanently non-authoritative.

## Authority walls

```text
Initiative Candidate ≠ Proposal
Proposal ≠ Authorization
Proposal ≠ Task
Proposal ≠ Schedule
Recommendation ≠ User Intent
Confidence ≠ Certainty
Prediction ≠ Permission
Eligibility ≠ Action
```

## Deliberate exclusions

M21.2 does not create tasks, schedule work, notify the user, select workers/plugins, grant authorization, execute capabilities, or mutate policy.

## Verification target

The focused M21.2 test suite must pass together with the full core regression suite. Verification is complete only after the local receipt is green.
