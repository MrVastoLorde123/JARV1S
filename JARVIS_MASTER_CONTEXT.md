# JARVIS Master Context

## Identity
JARVIS is the user's Third-Hand and Second-Brain: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning. It is not defined by one LLM, model, provider, interface, worker, or plugin.

## Core architectural invariants
- Everything is a plugin.
- Scraping and automation are backbone capabilities.
- JARVIS may change how it works without changing what it is authorized to do.
- JARVIS may revise what it believes without pretending prior history never existed.
- Intelligence ≠ Authority.
- Learning ≠ Authority.
- Adaptation ≠ Authorization.
- Capability ≠ Permission.
- Planning ≠ Execution.
- Proposal ≠ Authorization.
- Memory ≠ User Intent.
- Knowledge ≠ Truth.
- Confidence ≠ Certainty.
- Prediction ≠ Permission.

## Authority chain
```text
Reasoning
↓
Interpretation
↓
Prioritization
↓
Proposal
↓
Validation
↓
Policy
↓
Confirmation
↓
Confirmation Integrity
↓
Authorization
↓
Authorization Integrity
↓
Execution Preparation / Handoff
```

Identity chain:
`proposal_id → validation_id → policy_decision_id → confirmation_id → authorization_id → execution_id`

## Cognitive architecture
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
└────────────→ Learning
```

## Milestone state
- M19 Deep Personalization — VERIFIED / COMPLETE
- M20 Long-Horizon Task Management — VERIFIED / COMPLETE
- M21.1 Proactive Initiative Boundary — VERIFIED / COMPLETE (11/11 focused + 487/487 core)
- M21.2 Proactive Proposal Boundary — VERIFIED / COMPLETE (8/8 focused + 11/11 initiative + 487/487 core)
- M21.3 Proactive Value Assessment — VERIFIED / COMPLETE (7/7 focused + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.4 Information Gain / Uncertainty Reduction — VERIFIED / COMPLETE (7/7 focused + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.5 Bounded Proactive Scheduling / Notification — IMPLEMENTED / AWAITING LOCAL RECEIPT

## M21.3 verified semantics
Bounded deterministic advisory scoring uses importance, urgency, expected benefit, confidence, effort cost, and risk. Formula version is `linear-v1`; score is bounded to [0, 1]; ranking is deterministic by score descending and proposal identity ascending. Value assessment grants no authority and performs no scheduling, notification, assignment, or execution.

## M21.4 verified semantics
M21.4 estimates expected uncertainty reduction from additional information using bounded factors:
- current uncertainty
- expected reduction
- evidence quality
- relevance

Formula version: `multiplicative-v1`

`information_gain = current_uncertainty × expected_reduction × evidence_quality × relevance`

The result is advisory and bounded to [0, 1]. It does not establish truth or certainty and cannot authorize, schedule, notify, assign workers/plugins, create an execution request, execute capabilities, or mutate policy.

Boundary walls:
- Information Gain ≠ Truth
- Uncertainty Reduction ≠ Certainty
- Information Need ≠ User Intent
- Recommended Information ≠ Permission
- High Information Gain ≠ Authorization
- Ranking ≠ Scheduling

## M21.5 boundary
M21.5 may represent an advisory recommendation for when a proactive proposal could be surfaced and whether an operator-facing notification may be appropriate. It does not create an active scheduler entry or deliver a notification.

Current bounded contract:
- `ProactiveScheduleProposal` is immutable advisory metadata.
- `SchedulingEvaluation` distinguishes `PROPOSED`, `NEEDS_REVIEW`, and `NOT_SCHEDULABLE`.
- `NotificationChannel` makes the notification surface explicit.
- Time values must be timezone-aware.
- Notification messages are required when a channel is selected.
- Expiry cannot precede the proposed schedule time.
- Mapping identity must match the represented proposal identity.
- Ranking is deterministic by proposed time, then proposal identity.
- Inactive source proposals are not schedulable.
- Context explicitly reports `scheduled=False` and `notification_sent=False`.

M21.5 authority walls:
- Scheduling Proposal ≠ Scheduling
- Notification Recommendation ≠ Notification Delivery
- Timing ≠ Authorization
- Reminder Need ≠ User Intent
- Scheduling ≠ Permission
- Notification ≠ Execution
- Initiative ≠ Authorization

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
