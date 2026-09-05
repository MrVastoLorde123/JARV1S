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
Sandbox Admission
↓
Execution Preparation / Handoff
↓
Execution Attempt
↓
Outcome
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
- M22.3 Capability Lifecycle / Versioning Boundary — VERIFIED / COMPLETE (15/15 focused + 9/9 M22.2 + 8/8 M22.1 + 487/487 core)
- M22.4 Capability Permission / Policy Binding — VERIFIED / COMPLETE (9/9 focused + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core)
- M22.5 Plugin Isolation / Execution Sandbox — VERIFIED / COMPLETE (10/10 focused + 9/9 M22.4 + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core = 538/538)
- M22.6 Capability Discovery + Selection Integration — VERIFIED / COMPLETE (8/8 focused + 495/495 core regression)
- M22.7 Capability Proposal → Validated ToolRequest Boundary — VERIFIED / COMPLETE (7/7 request service + 8/8 invocation + 7/7 argument planner + 8/8 M22.6 integration + 4/4 catalog + 9/9 selection + 3/3 selection service + 502/502 core regression)
- M22.8 Explicit Authorization Boundary — VERIFIED / COMPLETE (9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression)
- M22.9 Authorization Integrity — VERIFIED / COMPLETE (9/9 integrity + 3/3 integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression = 544/544)
- M22.10 Sandbox Admission Integration — VERIFIED / COMPLETE (9/9 sandbox admission + 5/5 sandbox admission gate + 9/9 authorization integrity + 3/3 authorization integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression = 558/558)
- M22.11 Execution Preparation / Handoff Boundary — VERIFIED / COMPLETE (9/9 execution preparation + 4/4 execution preparation gate + 9/9 sandbox admission + 5/5 sandbox admission gate + 9/9 authorization integrity + 3/3 authorization integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression = 571/571)
- M22.12 Execution Attempt / Worker Boundary — VERIFIED / COMPLETE (11/11 execution attempt + 4/4 execution attempt gate + 9/9 execution preparation + 4/4 execution preparation gate + 9/9 sandbox admission + 5/5 sandbox admission gate + 9/9 authorization integrity + 3/3 authorization integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression = 583/583)
- M22.13 Execution Outcome / Result Integrity Boundary — VERIFIED / COMPLETE (12/12 focused + 502/502 core regression = 514/514)
- M22.14 Execution Outcome → Feedback Boundary — ACTIVE

## M22.14 direction
M22.14 establishes the first explicit feedback boundary after execution outcomes. A verified `ExecutionOutcome` may be transformed into an inert, provenance-bearing feedback event for later evaluation, correction, and learning, but feedback must not silently mutate authorization, request state, execute again, revoke capabilities, or write learning state directly.

Directional boundary:
```text
ExecutionOutcome
↓
Feedback Event
↓
Feedback Evaluation / Learning
```

M22.14 authority walls:
- Outcome ≠ Feedback
- Feedback ≠ Learning
- Feedback ≠ Authorization
- Feedback ≠ Execution
- Failure ≠ Revocation
- Feedback ≠ Retry Authorization
- Feedback evidence ≠ Truth

M22.14 should not add automatic retries, re-authorization, revocation, durable learning writes, or alternate execution paths.

## M22.13 verified semantics
M22.13 establishes the post-execution outcome boundary after the explicit execution-attempt layer. `ExecutionOutcomeService` binds an `ExecutionAttemptResult` to the exact `ExecutionHandoff`, re-checks execution identity, validates lifecycle consistency, and distinguishes tool-declared failure from executor failure. The resulting immutable `ExecutionOutcome` is suitable for later feedback and learning but grants no authority.

M22.13 verification receipt: **12/12 focused + 502/502 core regression tests passed locally = 514/514.**

Directional boundary:
```text
ExecutionHandoff
↓
Execution Attempt
↓
Outcome / Result Integrity
↓
Feedback / Learning
```

M22.13 authority walls:
- Execution Attempt ≠ Outcome Truth
- ToolResult ≠ Authorization
- ToolResult ≠ User Intent
- Outcome ≠ Learning
- Failure ≠ Revocation
- Successful execution ≠ Permission to execute again
- Outcome interpretation ≠ Policy bypass

M22.13 does not add retry policy, automatic re-authorization, revocation, durable outcome storage, learning writes, or alternate execution paths.

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
