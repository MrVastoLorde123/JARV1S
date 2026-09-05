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
- M22.5 Plugin Isolation / Execution Sandbox — IMPLEMENTED / AWAITING LOCAL RECEIPT

## M22.5 boundary
M22.5 establishes the execution-isolation boundary for plugins/capabilities. Sandbox profiles describe containment and resource constraints; admission evaluation determines whether the declared isolation contract is structurally admissible for the supported runtime. Neither creates permission, authorization, or execution.

Current bounded contract:
- `SandboxProfile` is immutable declarative containment/resource metadata.
- `IsolationMode` is bounded to `PROCESS` in this initial contract.
- `SandboxAdmissionEvaluator` performs deterministic contract admission only; it never launches or invokes a capability.
- `SandboxAdmissionResult` is immutable and carries an explicit `ADMISSIBLE` or `REJECTED` status.
- `SandboxProfileRegistry` provides explicit, conflict-aware registration and deterministic listing of sandbox profiles.
- Read-only filesystem profiles cannot declare writable paths.
- Resource constraints require positive timeout, memory, and CPU values; CPU is bounded to 100 percent.
- Sandbox context explicitly reports no permission, authority, authorization, or execution state.

M22.5 authority walls:
- Sandbox ≠ Authorization
- Isolation ≠ Trust
- Admission ≠ Permission
- Permission ≠ Execution
- Process Boundary ≠ Authority Boundary
- Containment ≠ Cancellation
- Capability ≠ Worker
- Plugin ≠ JARVIS

M22.5 does not spawn plugin subprocesses, execute arbitrary plugin code, convert sandbox admission into authorization, infer trust from isolation checks, grant permission, replace confirmation/authorization, revoke authorization, select workers, mutate policy, or bypass the existing validation → policy → confirmation → authorization chain.

## M22.4 verified semantics
M22.4 establishes bounded declarative permission/policy bindings for capabilities and specific capability versions. A binding describes whether a named permission is allowed or denied under a policy; it is not itself an authorization decision.

Current bounded contract:
- `CapabilityPermissionBinding` is immutable declarative metadata linking capability identity, permission, effect, optional version, and policy identity.
- `PermissionEffect` is bounded to `ALLOW` and `DENY`.
- Versioned and version-agnostic bindings are distinct and use M22.3 Semantic Versioning normalization when a version is supplied.
- `CapabilityPolicyBindingRegistry` provides explicit registration, deterministic lookup, and deterministic listing.
- Duplicate binding identities are rejected rather than silently replaced, preventing unresolved policy conflicts at the binding boundary.
- Binding context explicitly reports `permission_bound=True` while authority and authorization remain false.
- Policy-layer version validation preserves the M22.4 error boundary by converting lifecycle SemVer validation failures into `CapabilityPolicyError`.

M22.4 verification receipt: **9/9 focused + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core tests passed locally.**

M22.4 authority walls:
- Permission Binding ≠ Authorization
- Policy ≠ Authorization
- ALLOW ≠ Authorized
- DENY ≠ Execution Cancellation
- Active ≠ Permission
- Latest ≠ Authorized
- Trust ≠ Permission
- Permission ≠ Execution

M22.4 does not authorize an invocation, confirm user intent, execute capabilities, select workers, mutate policy, infer trust from permission, or convert an `ALLOW` binding into an execution request.

## M22.3 verified semantics
M22.3 establishes bounded capability version identity and lifecycle history. `SemanticVersion` enforces Semantic Versioning syntax and precedence; `CapabilityVersion` provides immutable version/lifecycle metadata; `CapabilityLifecycleRegistry` provides explicit version registration, lookup, forward-only lifecycle transitions, deterministic ordering, and retained history. Build metadata does not change SemVer precedence; a deterministic version-string tiebreaker is used when precedence is equal.

Lifecycle states are `ACTIVE`, `DEPRECATED`, and `RETIRED`. Allowed transitions are `ACTIVE → DEPRECATED → RETIRED` or `ACTIVE → RETIRED`; retired versions cannot be reactivated. `supersedes`, when present, must identify an older semantic version. `latest()` is metadata lookup only and excludes retired versions by default.

M22.3 verification receipt: **15/15 focused + 9/9 M22.2 + 8/8 M22.1 + 487/487 core tests passed locally.**

M22.3 authority walls:
- Version ≠ Identity Authority
- Lifecycle ≠ Permission
- Latest ≠ Authorized
- Active ≠ Trusted
- Deprecated ≠ Forbidden
- Retired ≠ Deleted
- Versioning ≠ Execution
- Capability ≠ Permission

M22.3 does not execute capabilities, grant permission, create authorization, infer trust from lifecycle state, infer authorization from `ACTIVE`, select workers, mutate policy, automatically replace versions, or delete retired history.

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
