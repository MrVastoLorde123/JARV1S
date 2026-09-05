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
Proactive Runtime / Feedback
↓
Capability Discovery / Selection
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
- M21.5 Bounded Proactive Scheduling / Notification — VERIFIED / COMPLETE (9/9 focused + 7/7 information gain + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.6 Proactive Runtime / Feedback Integration — VERIFIED / COMPLETE (10/10 runtime + 9/9 scheduling + 7/7 information gain + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M22 Capability / Plugin Ecosystem — ACTIVE
- M22.1 Capability / Plugin Contract + Registry Boundary — VERIFIED / COMPLETE (8/8 focused + 487/487 core)
- M22.2 Capability Trust / Provenance Boundary — VERIFIED / COMPLETE (9/9 focused + 8/8 M22.1 + 487/487 core)

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

## M21.5 verified semantics
M21.5 represents an advisory recommendation for when a proactive proposal could be surfaced and whether an operator-facing notification may be appropriate. It does not create an active scheduler entry or deliver a notification.

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

## M21.6 verified semantics
M21.6 composes bounded proactive outputs into one inspectable immutable runtime result and records outcome/feedback signals for later learning. It preserves initiative, proposal, value, information-gain, scheduling, and feedback identity; missing/non-eligible proposal state or non-proposed scheduling remains `NEEDS_REVIEW`.

Current bounded contract:
- `ProactiveFeedback` is immutable outcome metadata for an observed or not-observed result.
- `FeedbackOutcome` is bounded to `NOT_OBSERVED`, `ACCEPTED`, `DECLINED`, `EXPIRED`, `SUPERSEDED`, and `FAILED`.
- `ProactiveRuntimeResult` composes the M21 proactive stages into one inspectable immutable runtime result.
- All participating identities must agree on `proposal_id`; initiative candidate/trigger identity is preserved.
- Feedback cannot grant authority or mutate policy.
- Runtime context explicitly reports `authority_granted=False`, `authorization_granted=False`, `execution_requested=False`, and `executed=False`.
- Runtime ranking is deterministic by combined advisory value + information-gain score, then proposal identity.

## M22.1 verified semantics
M22.1 establishes the foundational contract and registry boundary for the plugin/capability ecosystem. A capability is a discoverable contract, not permission to invoke it.

Current bounded contract:
- `CapabilityDescriptor` is an immutable metadata-only description with stable capability identity, name, version, description, and metadata.
- `CapabilityRegistry` provides explicit, conflict-aware registration and deterministic discovery.
- Duplicate identities cannot silently replace existing registrations; replacement requires explicit `replace=True`.
- Discovery and lookup expose metadata only and never invoke registered capability code.
- Registry operations never invoke plugins, workers, schedulers, notifiers, or capabilities.
- Registration does not grant authorization, permission, trust, execution rights, or policy authority.
- Descriptor metadata is declarative; executable behavior remains outside the registry boundary.

M22.1 verification receipt: **8/8 focused + 487/487 core tests passed locally.**

M22.1 authority walls:
- Plugin ≠ JARVIS
- Capability ≠ Permission
- Registration ≠ Authorization
- Discovery ≠ Execution
- Manifest ≠ Trust
- Availability ≠ Permission
- Metadata ≠ Execution Request

M22.1 remains discovery/registry-only. Existing validation, policy, confirmation, authorization, and execution boundaries remain the only route to actual capability invocation.

## M22.2 boundary
M22.2 establishes the bounded provenance and trust-assessment layer for capabilities. Provenance records origin and supporting evidence; trust records an evidence-linked assessment. Neither creates permission or authorization.

Current bounded contract:
- `ProvenanceEvidence` is immutable structured evidence for provenance/trust claims.
- `CapabilityProvenance` is an immutable origin record bound to a capability identity.
- `CapabilityTrustAssessment` is immutable, evidence-linked metadata with bounded confidence in `[0, 1]`.
- `TrustStatus` is bounded to `UNASSESSED`, `CONDITIONAL`, `TRUSTED`, and `UNTRUSTED`.
- `UNASSESSED` must have zero confidence.
- Non-`UNASSESSED` trust assessments require supporting evidence.
- Trust assessments must validate against matching capability identity.
- Provenance and trust context explicitly report no authority, permission, authorization, or execution request.

M22.2 verification receipt: **9/9 focused + 8/8 M22.1 + 487/487 core tests passed locally.**

M22.2 authority walls:
- Provenance ≠ Trust
- Trust ≠ Permission
- Trust ≠ Authorization
- Evidence ≠ Truth
- Confidence ≠ Certainty
- Assessment ≠ Execution
- Capability ≠ Permission
- Registration ≠ Trust

M22.2 does not execute capabilities, grant permission, create authorization, infer execution authority from trust, mutate policy, schedule, notify, assign workers, or treat provenance as proof of truth.

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
