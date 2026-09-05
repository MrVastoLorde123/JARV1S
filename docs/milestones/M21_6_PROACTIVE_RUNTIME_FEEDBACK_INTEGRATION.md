# M21.6 — Proactive Runtime / Feedback Integration

## Purpose
M21.6 composes the bounded proactive stages into one inspectable runtime result and records outcome/feedback signals for later learning.

It is an integration boundary, not an autonomy boundary.

## Contract

```text
Initiative
   ↓
Initiative Evaluation
   ↓
Proposal
   ↓
Value Assessment
   ↓
Information Gain
   ↓
Scheduling Recommendation
   ↓
M21.6 Runtime Composition
   ↓
Outcome / Feedback Signal
   ↓
Future Learning

                         └── no bypass ──→ Validation → Confirmation → Authorization → Execution
```

## Core types

- `ProactiveFeedback` — immutable observed/not-observed outcome signal.
- `ProactiveRuntimeResult` — immutable composition of the M21 proactive stages.
- `RuntimeStatus` — `READY`, `NEEDS_REVIEW`, or `INCOMPLETE`.
- `FeedbackOutcome` — bounded vocabulary for later learning signals.
- `compose_proactive_runtime()` — deterministic composition with identity checks.
- `rank_runtime_results()` — deterministic advisory ranking only.

## Invariants

- Every component is type-checked before composition.
- Initiative, proposal, value, information-gain, scheduling, and feedback identities must agree.
- A missing proposal or non-eligible initiative remains `NEEDS_REVIEW`.
- A non-proposed scheduling evaluation remains `NEEDS_REVIEW`.
- Default feedback is explicitly `NOT_OBSERVED` and does not imply an outcome.
- Feedback may record outcomes but cannot grant authority or mutate policy.
- Runtime context explicitly reports `authority_granted=False`, `authorization_granted=False`, `execution_requested=False`, and `executed=False`.
- Ranking is deterministic by combined advisory value/information score, then proposal identity.
- No scheduler, notifier, worker, plugin, capability, authorization path, or policy mutator is invoked.

## Authority walls

```text
Runtime Integration ≠ Authorization
Feedback ≠ Truth
Outcome ≠ User Intent
Learning Signal ≠ Policy Change
Recommendation ≠ Execution
Recovery ≠ Execution
Integration ≠ Authority Escalation
```

## Deliberate exclusions

M21.6 does not:

- authorize a recommendation;
- confirm user intent;
- schedule or dispatch work;
- deliver notifications;
- invoke capabilities or plugins;
- assign workers;
- change policy;
- infer truth from feedback;
- automatically convert feedback into learned policy;
- execute any action.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

The milestone becomes VERIFIED / COMPLETE only after the user's local focused and regression test receipt passes.
