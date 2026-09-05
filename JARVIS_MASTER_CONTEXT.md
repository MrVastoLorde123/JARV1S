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
- M22.14 Execution Outcome → Feedback Boundary — VERIFIED / COMPLETE (10/10 focused + 502/502 core regression = 512/512)
- M22.15 Feedback Evaluation / Learning Candidate Boundary — VERIFIED / COMPLETE (9/9 focused + 502/502 core regression = 511/511)
- M22.16 Learning Decision Boundary — VERIFIED / COMPLETE (10/10 focused + 502/502 core regression = 512/512)
- M22.17 Learning Write Proposal Boundary — VERIFIED / COMPLETE (13/13 focused + 502/502 core regression = 515/515)
- M22.18 Learning Write Admission Boundary — VERIFIED / COMPLETE (12/12 focused + 502/502 core regression = 514/514)
- M22.19 Learning Write Execution Boundary — ACTIVE

## M22.19 direction
M22.19 establishes the controlled execution boundary between an admitted `LearningWriteProposal` and a replaceable learning writer. Only an `ADMITTED` write may proceed. The service binds admission, proposal, decision, and candidate identity, creates deterministic execution identity, passes an immutable request to the writer, and converts writer exceptions into an explicit immutable result.

Directional boundary:
```text
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
LearningDecisionService
↓
LearningDecision
↓
LearningWriteProposalService
↓
LearningWriteProposal
↓
LearningWriteAdmissionService
↓
LearningWriteAdmission
↓
LearningWriteExecutionService
↓
LearningWriteExecutionRequest
↓
LearningWriter
↓
LearningWriteExecutionResult
↓
Learning State / Memory
```

M22.19 authority walls:
- Learning Write Admission ≠ Learning Write Execution
- Learning Write Execution ≠ Authorization
- Learning Write Execution ≠ Tool Execution
- Learning Write Execution Result ≠ Learning Truth
- Learning ≠ Authority
- Completion ≠ Certainty

M22.19 should not grant authorization, bypass sandbox boundaries, invoke ordinary capability execution, retry failed writes, revoke permissions, or define concrete persistent learning stores.

## M22.18 verified semantics
M22.18 establishes the policy admission boundary between an inert `LearningWriteProposal` and any later learning-state or memory mutation. The admission service preserves exact proposal, decision, and candidate identity, applies explicit structural admission requirements, returns `ADMITTED` or `REJECTED`, and remains non-writing and non-authorizing.

M22.18 verification receipt: **12/12 focused + 502/502 core regression tests passed locally = 514/514.**

Directional boundary:
```text
LearningWriteProposal
↓
LearningWriteAdmissionService
↓
LearningWriteAdmission
↓
Learning / Memory Write Executor
```

M22.18 authority walls:
- Learning Write Proposal ≠ Learning Write Admission
- Learning Write Admission ≠ Learning Write
- Admission ≠ Authorization
- Admission ≠ Execution
- Learning ≠ Authority
- Confidence ≠ Certainty
- Evidence ≠ Truth
- Learning Domain ≠ Memory Domain

M22.18 baseline admission policy:
- proposal payload must not be empty;
- proposal evidence must be present;
- proposal provenance must be present;
- proposal confidence must be at least 0.5;
- policy identity is recorded with the immutable admission result.

M22.18 does not persist learning, mutate memory, authorize execution, trigger retries, revoke capabilities, or bypass existing memory decision/executor architecture.

## M22.17 verified semantics
M22.17 establishes the inert proposal boundary between an accepted `LearningDecision` and any later learning-state or memory mutation. An accepted decision may produce a structured `LearningWriteProposal`, while `DEFER` and `REJECT` produce no write proposal. The proposal preserves candidate provenance and identity, carries an explicit learning domain and payload, and remains non-writing, non-authorizing, and non-executing.

M22.17 verification receipt: **13/13 focused + 502/502 core regression tests passed locally = 515/515.**

## M22.16 verified semantics
M22.16 establishes the provider-neutral decision boundary between an inert `LearningCandidate` and any later learning or memory write. The decision preserves candidate identity, exposes confidence, distinguishes `ACCEPT`, `DEFER`, and `REJECT`, and remains non-authorizing and non-writing.

M22.16 verification receipt: **10/10 focused + 502/502 core regression tests passed locally = 512/512.**

## M22.15 verified semantics
M22.15 establishes the evaluation boundary between inert execution feedback and any learning or memory decision. `FeedbackEvaluationService` produces an immutable `LearningCandidate` with explicit signal classification, bounded confidence, and preserved feedback/execution/handoff provenance. Recursive evidence/provenance snapshots remain immutable.

M22.15 verification receipt: **9/9 focused + 502/502 core regression tests passed locally = 511/511.**

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
