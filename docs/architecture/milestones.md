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
Proactive Runtime / Feedback
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

### M21.5 — Bounded Proactive Scheduling / Notification
**Status: VERIFIED / COMPLETE.**

M21.5 represents when a proactive proposal could be surfaced and whether an operator-facing notification may be appropriate. It does not create an active scheduler entry and does not deliver a notification.

```text
ProactiveScheduleProposal — immutable advisory timing metadata
SchedulingEvaluation       — PROPOSED / NEEDS_REVIEW / NOT_SCHEDULABLE
NotificationChannel        — explicit channel semantics
```

Timezone-aware timestamps are required. Notification messages are required when a channel is selected. Expiry cannot precede the proposed schedule time. Evaluation identity must match the schedule proposal identity. Ranking is deterministic by proposed time, then proposal identity. Advisory context explicitly reports `scheduled=False` and `notification_sent=False`.

Boundary walls:

```text
Scheduling Proposal ≠ Scheduling
Notification Recommendation ≠ Notification Delivery
Timing ≠ Authorization
Reminder Need ≠ User Intent
Scheduling ≠ Permission
Notification ≠ Execution
Initiative ≠ Authorization
```

M21.5 does not create persistent scheduler entries, enqueue delayed work, send notifications, invoke capabilities/plugins, assign workers, create authorization, or mutate policy.

### M21.6 — Proactive Runtime / Feedback Integration
**Status: VERIFIED / COMPLETE.**

M21.6 composes initiative, proposal, value, information-gain, and scheduling outputs into one inspectable bounded runtime result and records outcome/feedback signals for later learning.

```text
Initiative → Proposal → Value → Information Gain
                         ↓
              Scheduling Recommendation
                         ↓
                Runtime Composition
                         ↓
                  Feedback / Outcome
                         ↓
                    Future Learning
```

Verified receipt: **10/10 runtime + 9/9 scheduling + 7/7 information gain + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core**.

The runtime preserves the existing authority chain and does not bypass validation, policy, confirmation, authorization, or execution. Feedback is an outcome signal, not a truth claim, user-intent claim, policy mutation, or authority grant.

Boundary walls:

```text
Runtime Integration ≠ Authorization
Feedback ≠ Truth
Outcome ≠ User Intent
Learning Signal ≠ Policy Change
Recommendation ≠ Execution
Recovery ≠ Execution
Integration ≠ Authority Escalation
```

## M22 — Capability / Plugin Ecosystem

M22 establishes a governed, extensible capability ecosystem while preserving the distinction between capability availability and permission to invoke it.

### M22.1 — Capability / Plugin Contract + Registry Boundary
**Status: VERIFIED / COMPLETE.**

M22.1 establishes immutable capability descriptors and a conflict-aware metadata registry. Discovery answers what capability exists; it does not grant permission to invoke it.

```text
Capability Descriptor
        ↓
Registry Registration
        ↓
Deterministic Discovery
        ↓
Proposal / Worker Selection
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

Boundary walls:

```text
Plugin ≠ JARVIS
Capability ≠ Permission
Registration ≠ Authorization
Discovery ≠ Execution
Manifest ≠ Trust
Availability ≠ Permission
Metadata ≠ Execution Request
```

M22.1 does not execute plugins, create authorization, grant permissions, establish trust, bypass validation/policy/confirmation/authorization, schedule, notify, assign workers, or mutate policy.

### M22.2 — Capability Trust / Provenance Boundary
**Status: VERIFIED / COMPLETE.**

M22.2 establishes immutable capability provenance records, structured evidence, and evidence-linked trust assessments. Provenance records where a capability came from; trust assessments describe the current evidence-backed trust state. Neither creates permission or authorization.

```text
Capability Descriptor
        ↓
Provenance Record
        ↓
Evidence
        ↓
Trust Assessment
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

Verified receipt: **9/9 M22.2 focused + 8/8 M22.1 focused + 487/487 core tests passed locally.**

Boundary walls:

```text
Provenance ≠ Trust
Trust ≠ Permission
Trust ≠ Authorization
Evidence ≠ Truth
Confidence ≠ Certainty
Assessment ≠ Execution
Capability ≠ Permission
Registration ≠ Trust
```

M22.2 does not execute capabilities, grant permission, create authorization, infer execution authority from trust, mutate policy, schedule, notify, select/assign workers, or treat provenance as proof of truth.

### M22.3 — Capability Lifecycle / Versioning
**Status: VERIFIED / COMPLETE.**

M22.3 establishes immutable capability version identities, lifecycle states, explicit forward-only lifecycle transitions, deterministic version ordering, and historical retention. Lifecycle/version metadata does not create trust, permission, authorization, or execution.

```text
Capability Descriptor
        ↓
Provenance / Trust
        ↓
Version Identity
        ↓
Lifecycle State
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

Verified receipt: **15/15 M22.3 focused + 9/9 M22.2 + 8/8 M22.1 + 487/487 core tests passed locally.**

Boundary walls:

```text
Version ≠ Identity Authority
Lifecycle ≠ Permission
Latest ≠ Authorized
Active ≠ Trusted
Deprecated ≠ Forbidden
Retired ≠ Deleted
Versioning ≠ Execution
Capability ≠ Permission
```

M22.3 does not execute capabilities, grant permission, create authorization, infer trust from lifecycle state, infer authorization from `ACTIVE`, select workers, mutate policy, automatically replace versions, or delete retired history.

### M22.4 — Capability Permission / Policy Binding
**Status: IMPLEMENTED / AWAITING LOCAL RECEIPT.**

M22.4 establishes immutable declarative permission/policy bindings for capabilities and optionally specific capability versions. A binding records whether a named permission is allowed or denied under a policy; it does not authorize an invocation.

```text
Capability Descriptor
        ↓
Provenance / Trust
        ↓
Version / Lifecycle
        ↓
Permission Binding
        ↓
Policy Context
        ↓
Validation / Policy Decision
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

Boundary walls:

```text
Permission Binding ≠ Authorization
Policy ≠ Authorization
ALLOW ≠ Authorized
DENY ≠ Execution Cancellation
Active ≠ Permission
Latest ≠ Authorized
Trust ≠ Permission
Permission ≠ Execution
```

M22.4 does not authorize invocations, confirm user intent, execute capabilities, select workers, mutate policy, infer trust from permission, or convert an `ALLOW` binding into an execution request.

### Future M22 boundaries

```text
M22.5 Plugin Isolation / Execution Sandbox
M22.6 Capability Discovery + Selection Integration
```

These remain directional until implemented and locally verified.

## Cross-cutting cognitive architecture

```text
Model ≠ JARVIS
LLM ≠ JARVIS
AI Provider ≠ JARVIS
Interface ≠ JARVIS
Plugin ≠ JARVIS
Worker ≠ JARVIS
```

JARVIS is a distributed cognitive architecture composed of bounded mechanisms for memory, knowledge, reasoning, uncertainty, prediction, planning, learning, feedback, initiative, capability discovery, and authority. Machine learning is an implementation technique, not the definition of intelligence.
