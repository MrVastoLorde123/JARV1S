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
- M22.13 Execution Outcome / Result Integrity Boundary — ACTIVE

## M22.13 direction
M22.13 establishes the boundary that interprets an execution attempt's returned result without confusing tool output with execution authority, completion truth, or learning. It should bind an `ExecutionAttemptResult` to the exact `ExecutionHandoff`, validate output identity and lifecycle consistency, distinguish transport/executor failure from tool-declared failure, and produce an immutable outcome record suitable for later feedback/learning without mutating authorization or the original request.

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

M22.13 should not add retry policy, automatic re-authorization, revocation, durable outcome storage, learning writes, or alternate execution paths.

## M22.12 verified semantics
M22.12 establishes the first explicit execution-attempt boundary after the inert `ExecutionHandoff`. `ExecutionAttemptService` accepts only a valid handoff, delegates through a replaceable `ToolExecutor`, produces a deterministic `execution_id`, and returns explicit completed/failed attempt state. Executor output must match the exact handoff tool and invocation identity.

M22.12 verification receipt: **11/11 execution attempt + 4/4 execution attempt gate + 9/9 execution preparation + 4/4 execution preparation gate + 9/9 sandbox admission + 5/5 sandbox admission gate + 9/9 authorization integrity + 3/3 authorization integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression tests passed locally = 583/583.**

Directional boundary:
```text
ExecutionHandoff
↓
Execution Attempt / Worker Boundary
↓
Execution
↓
Outcome
```

M22.12 authority walls:
- Execution Preparation ≠ Execution Attempt
- Execution Attempt ≠ Successful Outcome
- Execution Attempt ≠ Worker Identity
- Worker Assignment ≠ Authorization
- Execution Attempt ≠ Capability Permission
- Outcome ≠ Authorization

M22.12 does not silently bypass `PolicyGate`, re-authorize requests from scratch, mutate the original handoff, grant permissions, or collapse execution attempt, worker assignment, and outcome into one undifferentiated operation.

## M22.11 verified semantics
M22.11 establishes the final non-executing boundary immediately before tool execution. A request may reach execution preparation only after authorization, authorization integrity, and sandbox admission all succeed. The immutable `ExecutionHandoff` preserves request identity, upstream evidence, sandbox identity, and arguments while remaining explicitly non-executing.

M22.11 verification receipt: **9/9 execution preparation + 4/4 execution preparation gate + 9/9 sandbox admission + 5/5 sandbox admission gate + 9/9 authorization integrity + 3/3 authorization integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression tests passed locally = 571/571.**

Directional boundary:
```text
Validated ToolRequest
↓
Policy
↓
Confirmation
↓
AuthorizationDecision
↓
Authorization Integrity
↓
Sandbox Profile Resolution
↓
Sandbox Admission
↓
Execution Preparation / Handoff
↓
Execution
```

M22.11 authority walls:
- Sandbox Admission ≠ Execution Preparation
- Execution Preparation ≠ Execution
- Execution Preparation ≠ Worker Assignment
- Execution Preparation ≠ Process Launch
- Execution Preparation ≠ Containment Activation
- Upstream authorization evidence ≠ fresh authorization
- Preparation ≠ permission escalation

M22.11 does not introduce process spawning, worker allocation, sandbox activation, plugin execution, durable authorization storage, revocation/expiration, or an alternate bypass around `PolicyGate`.

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
