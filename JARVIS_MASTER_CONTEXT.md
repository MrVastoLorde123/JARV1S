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
- M22.3 Capability Lifecycle / Versioning Boundary — VERIFIED / COMPLETE (15/15 focused + 9/9 M22.2 + 8/8 M22.1 + 487/487 core)
- M22.4 Capability Permission / Policy Binding — VERIFIED / COMPLETE (9/9 focused + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core)
- M22.5 Plugin Isolation / Execution Sandbox — VERIFIED / COMPLETE (10/10 focused + 9/9 M22.4 + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core = 538/538)
- M22.6 Capability Discovery + Selection Integration — VERIFIED / COMPLETE (8/8 focused + 495/495 core regression)
- M22.7 Capability Proposal → Validated ToolRequest Boundary — VERIFIED / COMPLETE (7/7 request service + 8/8 invocation + 7/7 argument planner + 8/8 M22.6 integration + 4/4 catalog + 9/9 selection + 3/3 selection service + 502/502 core regression)
- M22.8 Explicit Authorization Boundary — VERIFIED / COMPLETE (9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression)
- M22.9 Authorization Integrity — VERIFIED / COMPLETE (9/9 integrity + 3/3 integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression = 544/544)
- M22.10 Sandbox Admission Integration — ACTIVE

## M22.10 direction
M22.10 integrates the existing sandbox admission contract into the post-authorization path. A granted, integrity-verified request must resolve to an explicit sandbox profile and pass deterministic sandbox admission before execution can be delegated. Admission remains metadata-only: it does not grant authorization, activate containment, launch a worker, or execute a plugin.

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
```

M22.10 authority walls:
- Authorization ≠ Sandbox Admission
- Authorization Integrity ≠ Sandbox Admission
- Sandbox Admission ≠ Execution
- Sandbox Profile ≠ Permission
- Sandbox Admission ≠ Worker Assignment
- Sandbox Admission ≠ Containment Activation

M22.10 does not launch processes, activate containment, execute plugins, assign workers, persist authorization, add revocation/expiration, or bypass `PolicyGate`.

## M22.9 verified semantics
M22.9 establishes the integrity boundary between an explicit `AuthorizationDecision` and execution. `AuthorizationIntegrityService` deterministically binds a granted authorization to the exact `ToolRequest` through request and decision fingerprints plus tool/invocation identity checks. `PolicyGate.invoke()` verifies that integrity before delegating to `ToolService`.

M22.9 verification receipt: **9/9 integrity + 3/3 integrity gate + 9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression tests passed locally.**

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
Sandbox
↓
Execution
```

M22.9 authority walls:
- Authorization ≠ Authorization Integrity
- Authorization Integrity ≠ Execution
- Validated ToolRequest ≠ Authorized ToolRequest
- Authorization ≠ Permission
- Authorization ≠ Sandbox Admission

M22.9 does not implement durable authorization storage, revocation, expiration policy, distributed consensus, worker assignment, sandbox admission, or plugin execution.

## M22.8 verified semantics
M22.8 makes the authority transition from a validated `ToolRequest` to an explicit immutable `AuthorizationDecision`. `ExplicitAuthorizationService` evaluates the existing policy contract and, when required, the existing confirmation contract. `PolicyGate.authorize()` exposes authorization without execution; `PolicyGate.invoke()` consumes that decision before delegating to `ToolService`.

M22.8 verification receipt: **9/9 authorization + 6/6 authorization gate + 15/15 legacy gate + 502/502 core regression tests passed locally.**

Directional boundary:
```text
Validated ToolRequest
↓
Policy
↓
Confirmation (when required)
↓
Explicit AuthorizationDecision
↓
Sandbox
↓
Execution
```

M22.8 authority walls:
- Validated ToolRequest ≠ Authorized ToolRequest
- Policy ALLOW ≠ Implicit Execution
- Confirmation ≠ Execution
- Authorization ≠ Execution
- Permission ≠ Authorization
- Sandbox ≠ Authorization

M22.8 does not execute tools from `authorize()`, bypass `PolicyGate`, infer authorization from selection/argument generation/trust/lifecycle/permission/sandbox state, assign workers, or add authorization persistence/revocation.

## M22.7 verified semantics
M22.7 binds M22.6 capability selection to the existing structural invocation boundary without granting execution authority. `CapabilityRequestProposalService` accepts an immutable `CapabilityDiscoverySelection`, requires any selected candidate to originate from that exact snapshot, asks a replaceable `CapabilityArgumentPlanner` for inert argument data, and uses `CapabilityInvocationBuilder` to structurally validate and materialize a `ToolRequest`.

M22.7 verification receipt: **7/7 request service + 8/8 invocation + 7/7 argument planner + 8/8 M22.6 integration + 4/4 catalog + 9/9 selection + 3/3 selection service + 502/502 core regression tests passed locally.**

Directional boundary:
```text
CapabilityDiscoverySelection
↓
CapabilityRequestProposalService
↓
CapabilityArgumentPlanner
↓
CapabilityInvocationBuilder
↓
CapabilityRequestProposal
↓
Validation / Policy
↓
Confirmation
↓
Authorization
↓
Sandbox
↓
Execution
```

M22.7 authority walls:
- Selection ≠ Request Authorization
- Argument Proposal ≠ Execution
- Validated ToolRequest ≠ Authorized ToolRequest
- ToolRequest ≠ Tool Execution
- Capability ≠ Worker
- Permission ≠ Authorization
- Sandbox ≠ Authorization

M22.7 does not invoke tools or plugins, authorize a proposal, interpret argument generation as confirmation, bypass `PolicyGate`, grant permission, perform sandbox admission, assign workers, or create an execution request merely because a request was structurally validated.

## M22.6 verified semantics
M22.6 establishes the explicit provider-neutral capability discovery and selection integration boundary. `CapabilityCatalog` remains a read-only view over the existing `ToolCapabilityGateway`; `CapabilitySelectionService` composes discovery and selector ranking; `CapabilityDiscoverySelection` captures the exact discovered capabilities and the selection derived from that snapshot.

The deterministic selector remains the current dependency-free fallback, while the selector contract stays replaceable for future model-backed implementations. Selection remains a proposal operation and cannot invoke tools.

M22.6 verification receipt: **8/8 focused integration + 495/495 core regression tests passed locally.**

Directional boundary:
```text
ToolCapabilityGateway
↓
CapabilityCatalog
↓
CapabilitySelectionService
↓
CapabilitySelector
↓
CapabilityDiscoverySelection
↓
Structured Proposal
↓
Validation / Policy
↓
Confirmation
↓
Authorization
↓
Sandbox
↓
Execution
```

M22.6 authority walls:
- Discovery ≠ Permission
- Selection ≠ Authorization
- Selection ≠ Execution
- Capability ≠ Permission
- Capability ≠ Worker
- Proposal ≠ Authorization
- Sandbox ≠ Authorization
- Policy ≠ Authorization

M22.6 does not invoke tools or plugins, construct a privileged execution path, authorize selected capabilities, interpret selection as confirmation, bypass `PolicyGate`, assign workers, infer trust/permission/authorization from rank, mutate registries or policy, or perform sandbox admission.

## Learning architecture
Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mathematical mechanisms are selected by problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## Memory taxonomy
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## GitHub session protocol
Every GitHub engineering session begins by reading this file from the current working branch/ref. Before moving to the next milestone, update this file with the newest verified receipt, implementation state, architecture boundary, and next active milestone. Never assume a remembered milestone state is newer than this repository ledger.

## Verification rule
A milestone is not considered GREEN / VERIFIED / COMPLETE until the user provides the local test receipt. Remote implementation status is kept distinct from local verification status.
