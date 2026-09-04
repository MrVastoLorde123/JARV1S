# M21.1 — Proactive Initiative Boundary

## Purpose

M20 established bounded long-horizon continuation for work already represented as a goal, objective, and task graph. The updated JARVIS architecture now treats proactive behavior as part of a larger cognitive loop rather than as a direct trigger-to-action mechanism.

M21.1 therefore defines the first proactive boundary while preserving the new cognitive and epistemic structure:

```text
Signal / Observation
        ↓
Evidence + Provenance
        ↓
Context / World Model
        ↓
Reasoning / Uncertainty
        ↓
Initiative Candidate
        ↓
Evaluation
        ↓
[future Proposal]
        ↓
[existing Authority Chain]
```

M21.1 implements only the trigger, bounded candidate, and deterministic evaluation layers. The later stages remain separate milestones.

## Cognitive architecture fit

M21.1 does not attempt to "make JARVIS intelligent" by adding an LLM or an opaque scoring model. It establishes a clean input boundary that later cognitive mechanisms can reason over.

The trigger preserves **signal provenance**, not truth. Evidence identities can be carried into later reasoning without being silently promoted to facts.

```text
Signal ≠ Evidence
Evidence ≠ Truth
Trigger ≠ User Intent
Eligibility ≠ Action
```

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

An immutable bounded candidate that says, in effect, **"this may deserve consideration."**

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

## Deterministic rules

1. Candidate and trigger identities must match.
2. Explicit suppression wins before other dispositions.
3. Expiry is evaluated at a supplied, timezone-aware evaluation time.
4. Review requests produce `NEEDS_REVIEW` and do not bypass the boundary.
5. Otherwise the candidate is `ELIGIBLE` for a later proposal-stage decision.
6. No function in M21.1 creates tasks, schedules work, notifies the user, grants authorization, or executes anything.

## Why this boundary comes first

Proactivity becomes dangerous when a system collapses these stages:

```text
noticed something
      ↓
therefore it is true
      ↓
therefore the user wants it
      ↓
therefore it should happen
      ↓
therefore I may do it
```

M21.1 intentionally prevents that collapse.

The future M21 architecture may use probabilistic reasoning, learned preferences, temporal models, optimization, information-gain measures, or model-assisted reasoning to improve candidate quality. None of those mechanisms will remove the boundary between cognition and authority.

## Authority walls

```text
Trigger ≠ User Intent
Initiative Candidate ≠ Proposal
Initiative Candidate ≠ Authorization
Proactive Evaluation ≠ Permission
Signal ≠ Evidence
Evidence ≠ Truth
Eligibility ≠ Action
Proactivity ≠ Autonomous Agency
```

## Test receipt

Focused M21.1 tests cover immutability, metadata isolation, identity binding, expiry, suppression precedence, review handling, and authority/execution absence.

Verification is considered complete only after the local focused test suite and full core regression are green.
