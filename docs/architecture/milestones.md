# JARVIS Milestone Architecture

This document defines the architectural progression of JARVIS. Milestone names may evolve, but the boundaries and invariants are authoritative. The cognitive architecture introduced here applies retroactively to existing intelligence work and prospectively to M21+.

## M20 — Long-Horizon Task Management

Establishes bounded long-horizon work representation and runtime:

```text
Goal → Objective → Task → Dependency Graph → Progress / Evidence
→ Long-Horizon Plan → Next-Step Proposal → Persistence / Recovery → Runtime
```

**Status: VERIFIED / COMPLETE.**

## M21 — Proactive JARVIS

M21 extends JARVIS from reacting to explicit requests toward bounded proactive cognition.

```text
Environment / User
        ↓
Perception / Input
        ↓
Evidence + Provenance
        ↓
Memory + Personal Knowledge
        ↓
World Model / Current Context
        ↓
Reasoning + Uncertainty
        ↓
Initiative Candidate
        ↓
Initiative Evaluation
        ↓
Proactive Proposal
        ↓
Value Assessment
        ↓
Information Gain / Uncertainty Reduction
        ↓
Bounded Scheduling / Notification Proposal
        ↓
Prioritization
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution / Capabilities
        ↓
Outcome / Feedback
        └──────────────→ Learning
```

### M21.1 — Proactive Initiative Boundary
**Status: VERIFIED / COMPLETE.**

A signal may create an initiative candidate without becoming a task, proposal, authorization, notification, schedule, or execution request.

### M21.2 — Proactive Proposal Boundary
**Status: VERIFIED / COMPLETE.**

An eligible initiative candidate may become an immutable proposal preserving candidate/trigger identity and evidence provenance. Proposal formation grants no authority.

### M21.3 — Proactive Value Assessment
**Status: VERIFIED / COMPLETE.**

A bounded deterministic advisory score uses importance, urgency, expected benefit, confidence, effort cost, and risk. Formula version: `linear-v1`. Score is bounded to [0, 1], and ranking is deterministic by score descending then `proposal_id` ascending.

### M21.4 — Information Gain / Uncertainty Reduction
**Status: VERIFIED / COMPLETE.**

M21.4 estimates how much additional information could reduce uncertainty around a proactive proposal. Factors are current uncertainty, expected reduction, evidence quality, and relevance. Formula version: `multiplicative-v1`.

```text
information_gain = current_uncertainty
                 × expected_reduction
                 × evidence_quality
                 × relevance
```

The estimate is advisory and bounded to [0, 1]. It does not establish truth or certainty and cannot create authority, permission, scheduling, notification, worker/plugin assignment, execution requests, execution, or policy changes.

Boundary walls:

```text
Information Gain ≠ Truth
Uncertainty Reduction ≠ Certainty
Information Need ≠ User Intent
Recommended Information ≠ Permission
High Information Gain ≠ Authorization
Ranking ≠ Scheduling
```

### M21.5 — Bounded Proactive Scheduling / Notification
**Status: IMPLEMENTED / AWAITING LOCAL RECEIPT.**

M21.5 represents when a proactive proposal could be surfaced and whether an operator-facing notification may be appropriate. It does not create an active scheduler entry and does not deliver a notification.

The bounded contract includes:

```text
ProactiveScheduleProposal — immutable advisory timing metadata
SchedulingEvaluation       — PROPOSED / NEEDS_REVIEW / NOT_SCHEDULABLE
NotificationChannel        — explicit channel semantics
```

Timezone-aware timestamps are required. Notification messages are required when a channel is selected. Expiry cannot precede the proposed time. Identity must remain consistent between an evaluation and its schedule proposal. Ranking is deterministic by proposed time, then proposal identity.

```text
Scheduling Proposal ≠ Scheduling
Notification Recommendation ≠ Notification Delivery
Timing ≠ Authorization
Reminder Need ≠ User Intent
Scheduling ≠ Permission
Notification ≠ Execution
Initiative ≠ Authorization
```

The context surface explicitly reports `scheduled=False` and `notification_sent=False`.

### Future M21 boundary

```text
M21.6 Proactive Runtime / Feedback Integration
```

No M21 stage may grant authority merely because behavior is proactive, predictive, useful, information-seeking, scheduled-looking, or notification-oriented.

## Cross-cutting cognitive architecture

```text
Model ≠ JARVIS
LLM ≠ JARVIS
AI Provider ≠ JARVIS
Interface ≠ JARVIS
Plugin ≠ JARVIS
Worker ≠ JARVIS
```

JARVIS is a distributed cognitive architecture composed of bounded mechanisms for memory, knowledge, reasoning, uncertainty, prediction, planning, learning, feedback, initiative, and authority. Machine learning is an implementation technique, not the definition of intelligence.
