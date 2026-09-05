# M21.5 — Bounded Proactive Scheduling / Notification

## Purpose

M21.5 gives proactive cognition a bounded representation for **when a recommendation could be surfaced** and **whether an operator-facing notification may be appropriate**.

It does not activate a scheduler, enqueue a job, deliver a notification, or grant permission to do either.

## Contract

```text
Proactive Proposal
      ↓
Scheduling Recommendation
      ↓
[Validation / Policy]
      ↓
Confirmation
      ↓
Authorization
      ↓
Actual scheduler / notifier
```

M21.5 stops at the scheduling recommendation boundary.

## Core types

- `ProactiveScheduleProposal` — immutable advisory timing and notification metadata.
- `SchedulingEvaluation` — immutable result with `PROPOSED`, `NEEDS_REVIEW`, or `NOT_SCHEDULABLE` status.
- `NotificationChannel` — explicit notification channel vocabulary.

## Invariants

- All timestamps are timezone-aware.
- A notification message is required when a notification channel is selected.
- An expiry time cannot precede the proposed schedule time.
- Evaluation identity must match the schedule proposal identity.
- Advisory context explicitly reports `scheduled=False` and `notification_sent=False`.
- Ranking is deterministic by proposed time, then `proposal_id`.
- Non-active source proposals are not schedulable.
- No scheduler, notifier, worker, plugin, or capability is invoked by this module.

## Authority walls

```text
Scheduling Proposal ≠ Scheduling
Notification Recommendation ≠ Notification Delivery
Timing ≠ Authorization
Reminder Need ≠ User Intent
Scheduling ≠ Permission
Notification ≠ Execution
Initiative ≠ Authorization
```

## Deliberate exclusions

M21.5 does not:

- create persistent scheduler entries;
- enqueue delayed work;
- send or dispatch notifications;
- invoke capabilities or plugins;
- assign workers;
- create authorization;
- mutate policy;
- infer that a timing recommendation constitutes user consent.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

The milestone becomes VERIFIED / COMPLETE only after the user's local focused and regression test receipt passes.
