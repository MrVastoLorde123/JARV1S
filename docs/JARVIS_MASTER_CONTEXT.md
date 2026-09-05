# JARVIS Master Context

> Canonical cross-chat continuity document for the JARVIS project.
>
> This is the single source-of-truth context document. Read it first at the start of every engineering session, then inspect the current branch/repository state. Repository code and tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's **Third-Hand + Second-Brain**: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning.

It is not defined by one LLM, model, provider, interface, worker, or plugin. It is not primarily a product to sell. Its purpose is to help the user create products and innovations, turn thoughts into words and words into the future, and eventually understand intent so well that explicit instructions become less necessary.

Core long-term loop:

`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Two complementary halves from the original roadmap:

- **Third Hand:** action, execution, automation, inspection, modification, verification.
- **Second Brain:** memory, relationships, persistent projects, self-evaluation, initiative, and compounding knowledge/context.

## 2. Core architectural invariants

- Everything is a capability/plugin.
- Scraping and automation are backbone capabilities.
- JARVIS core orchestrates; capabilities implement.
- JARVIS may change how it works without changing what it is authorized to do.
- JARVIS may revise what it believes without pretending prior history never existed.
- Model intelligence is advisory; deterministic boundaries retain authority over execution.
- Safety is structural, not prompt-only.
- Prefer explicit contracts over magic behavior.
- Prefer composition over special cases.
- Prefer a small core with extensible capabilities over a monolithic agent.
- Prefer existing reliable mechanisms over reinventing infrastructure.
- Local-first remains a core architectural preference.

Non-negotiable separations:

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

### Authority chain

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

Learning/write authority chain:

```text
Execution Outcome
↓
Execution Feedback
↓
Feedback Evaluation
↓
Learning Candidate
↓
Learning Decision
↓
Learning Write Proposal
↓
Learning Write Admission
↓
Learning Write Execution
↓
Learning State / Memory Mutation
```

The final write/mutation boundary is deliberately downstream from reasoning, evidence, and learning decisions.

## 3. Cognitive architecture

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

Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning. Mechanisms should fit the problem: probability/Bayesian reasoning, graphs, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback.

## 4. Repository

GitHub:

`https://github.com/MrVastoLorde123/JARV1S.git`

The real local project directory is:

`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion was a workflow mistake and is considered resolved. Do not resurrect that issue without new evidence.

## 5. Current verified state

Current milestone branch:

`feature/m22.19-learning-write-execution-boundary`

Latest verified local receipt:

- **M22.19:** 12/12 focused + 502/502 core regression = **514/514**

The user-provided receipt for M22.19 is the verification authority for this milestone.

Previously verified checkpoints:

- **M22.18:** 12/12 focused + 502/502 core = 514/514
- **M22.17:** 13/13 focused + 502/502 core = 515/515
- **M22.16:** 10/10 focused + 502/502 core = 512/512
- **M22.15:** 9/9 focused + 502/502 core = 511/511
- **M22.14:** 10/10 focused + 502/502 core = 512/512
- **M22.13:** 12/12 focused + 502/502 core = 514/514
- **M22.12:** 11/11 execution-attempt + 4/4 gate plus prior coverage = 583/583
- **M22.11:** 571/571
- **M22.10:** 558/558
- **M22.9:** 544/544
- **M22.8:** 9/9 authorization + 6/6 gate + 15/15 legacy + 502/502 core
- **M22.7:** 502/502 core regression with focused capability-request coverage
- Earlier M21 proactive milestones were locally verified according to the milestone ledger below.

## 6. Milestone state

- M19 Deep Personalization — VERIFIED / COMPLETE
- M20 Long-Horizon Task Management — VERIFIED / COMPLETE
- M21.1 Proactive Initiative Boundary — VERIFIED / COMPLETE (11/11 focused + 487/487 core)
- M21.2 Proactive Proposal Boundary — VERIFIED / COMPLETE (8/8 focused + 11/11 initiative + 487/487 core)
- M21.3 Proactive Value Assessment — VERIFIED / COMPLETE (7/7 focused + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.4 Information Gain / Uncertainty Reduction — VERIFIED / COMPLETE (7/7 focused + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.5 Bounded Proactive Scheduling / Notification — VERIFIED / COMPLETE (9/9 focused + 7/7 information gain + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M21.6 Proactive Runtime / Feedback Integration — VERIFIED / COMPLETE (10/10 runtime + 9/9 scheduling + 7/7 information gain + 7/7 value + 8/8 proposal + 11/11 initiative + 487/487 core)
- M22 Capability / Plugin Ecosystem — ACTIVE
- M22.1 Capability / Plugin Contract + Registry Boundary — VERIFIED / COMPLETE
- M22.2 Capability Trust / Provenance Boundary — VERIFIED / COMPLETE
- M22.3 Capability Lifecycle / Versioning Boundary — VERIFIED / COMPLETE
- M22.4 Capability Permission / Policy Binding — VERIFIED / COMPLETE
- M22.5 Plugin Isolation / Execution Sandbox — VERIFIED / COMPLETE (538/538)
- M22.6 Capability Discovery + Selection Integration — VERIFIED / COMPLETE (8/8 focused + 495/495 core regression)
- M22.7 Capability Proposal → Validated ToolRequest Boundary — VERIFIED / COMPLETE (502/502 core regression)
- M22.8 Explicit Authorization Boundary — VERIFIED / COMPLETE
- M22.9 Authorization Integrity — VERIFIED / COMPLETE (544/544)
- M22.10 Sandbox Admission Integration — VERIFIED / COMPLETE (558/558)
- M22.11 Execution Preparation / Handoff Boundary — VERIFIED / COMPLETE (571/571)
- M22.12 Execution Attempt / Worker Boundary — VERIFIED / COMPLETE (583/583)
- M22.13 Execution Outcome / Result Integrity Boundary — VERIFIED / COMPLETE (514/514)
- M22.14 Execution Outcome → Feedback Boundary — VERIFIED / COMPLETE (512/512)
- M22.15 Feedback Evaluation / Learning Candidate Boundary — VERIFIED / COMPLETE (511/511)
- M22.16 Learning Decision Boundary — VERIFIED / COMPLETE (512/512)
- M22.17 Learning Write Proposal Boundary — VERIFIED / COMPLETE (515/515)
- M22.18 Learning Write Admission Boundary — VERIFIED / COMPLETE (514/514)
- M22.19 Learning Write Execution Boundary — VERIFIED / COMPLETE (514/514)

## 7. M22 learning architecture and authority walls

### M22.15 — Learning Candidate

`FeedbackEvaluationService` converts inert execution feedback into an immutable `LearningCandidate` carrying signal classification, confidence, evidence, and provenance. It does not write learning, mutate memory, re-authorize, retry, revoke, or execute.

### M22.16 — Learning Decision

`LearningDecisionService` consumes a `LearningCandidate` and produces an immutable `LearningDecision` with explicit `ACCEPT`, `DEFER`, or `REJECT` semantics. The decision remains non-writing and non-authorizing.

Authority walls:

- Learning Candidate ≠ Learning Decision
- Learning Decision ≠ Learning Write
- Learning Decision ≠ Memory Mutation
- Learning ≠ Authority
- Confidence ≠ Certainty
- Evidence ≠ Truth
- Learning Decision ≠ Retry Authorization
- Learning Decision ≠ Execution

### M22.17 — Learning Write Proposal

`LearningWriteProposalService` converts only an `ACCEPT` decision into an inert, immutable `LearningWriteProposal`. `DEFER` and `REJECT` produce no proposal.

The proposal carries an explicit learning domain, payload, evidence, provenance, confidence, and exact decision/candidate lineage. It cannot authorize, execute, retry, revoke, or mutate memory.

### M22.18 — Learning Write Admission

`LearningWriteAdmissionService` evaluates proposal structure and policy conditions before mutation. The deterministic baseline requires non-empty payload, evidence, provenance, and confidence of at least 0.5. It returns `ADMITTED` or `REJECTED` and remains non-writing/non-authorizing.

### M22.19 — Learning Write Execution

`LearningWriteExecutionService` is the controlled execution boundary after admission. Only an `ADMITTED` proposal can produce a write request. The request is immutable and identity-bound; a replaceable `LearningWriter` performs the actual write; writer failures become explicit immutable results.

M22.19 walls:

- Learning Write Admission ≠ Learning Write Execution
- Learning Write Execution ≠ Authorization
- Learning Write Execution ≠ Tool Execution
- Learning Write Execution Result ≠ Learning Truth
- Learning ≠ Authority
- Completion ≠ Certainty

M22.19 does not grant authorization, bypass sandbox boundaries, invoke ordinary capability execution, retry failed writes, revoke permissions, or define concrete persistent learning stores.

## 8. Existing memory decision/write architecture

The existing memory system already separates **decision** from **mutation**:

- `MemoryDecisionContext` describes the information available when deciding what should happen to a memory candidate.
- `MemoryDecision` is the structured decision record.
- `MemoryDecisionProvider` is provider-neutral and explicitly non-mutating.
- `MemoryDecisionService` selects/validates a provider and does not persist anything.
- `MemoryDecisionExecutor` is the mutation boundary that performs CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE operations.

This architecture must remain distinct from learning decision/admission/execution layers. Learning may eventually map to memory actions, but it must not bypass the memory decision/executor contract.

Memory taxonomy:

`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## 9. Capability/plugin ecosystem foundation

### Capability contract and registry

`CapabilityDescriptor` is immutable, metadata-only capability identity. `CapabilityRegistry` performs deterministic registration, conflict handling, unregister, get, and discover. Registration is not authorization and discovery is not execution.

### Capability trust / provenance

Capability provenance and trust are separate concepts. Non-UNASSESSED trust requires evidence. Trust does not imply permission, authorization, or execution rights.

### Capability lifecycle / versioning

Capabilities use explicit semantic versioning and lifecycle state. ACTIVE, DEPRECATED, and RETIRED are distinct. Retirement is not reversible by accidental reactivation; latest-version discovery excludes retired versions by default.

### Permission / policy binding

Capability permission bindings are explicit and conflict-aware. Permission binding is not authorization; ALLOW is not equivalent to an authorized execution.

### Sandbox

Sandbox profiles are declarative containment/resource profiles. Admission is a distinct step from authorization and execution. Process isolation is not an authority boundary.

### Discovery / selection

`CapabilityCatalog` provides a read-only deterministic snapshot. `CapabilitySelector` and `CapabilitySelectionService` rank/select available capabilities. Discovery and selection remain advisory and non-executing.

### Proposal / invocation

`CapabilityRequestProposal`, argument planning, and invocation building establish a deterministic path from capability selection to a validated `ToolRequest`. Model-proposed arguments remain advisory until deterministic validation succeeds.

### Authorization / integrity / execution

The capability execution path now explicitly separates:

`proposal → validation → policy → confirmation → authorization → authorization integrity → sandbox admission → execution preparation → execution attempt → outcome → feedback`

Each stage preserves exact identity and refuses to silently inherit authority from an earlier or adjacent concept.

## 10. Workspace capability — frozen

The workspace subsystem is considered architecturally approved/frozen unless a real architectural need appears.

Capabilities:

- `read_file`
- `list_directory`
- `search_files`
- `write_file`

Shared workspace behavior covers path resolution, workspace confinement, workspace-relative POSIX reporting, traversal rules, hidden-entry behavior, symlink handling, filesystem-error normalization, and limits.

Risk boundary:

- read/list/search are low-risk and read-only
- `write_file` is high-risk and confirmation-gated

Workspace composition has been treated as one coherent capability surface:

`discover → inspect → search → modify`

## 11. Tool capability bridge — completed foundation

Core defines the minimal abstraction needed to invoke tools safely:

- `ToolInvoker`
- `ToolCapabilityGateway`
- `ToolPlanStepHandler`

JARVIS receives the tool-facing capability boundary by dependency injection instead of constructing concrete tool infrastructure inside `jarvis.py`.

Representative execution flow:

`JARVIS → TaskRequest → ExecutionPlanner → PlanValidator → ExecutionPolicy → PlanExecutor → ToolPlanStepHandler → ToolInvoker → PolicyGate → ToolService → ToolHandler`

The core execution policy does not duplicate concrete tool risk. Capability-specific policy belongs at the tool/capability boundary.

## 12. Natural-language routing groundwork — historical/current integration track

Original routing groundwork introduced:

- `RequestIntent`
- `RequestIntentClassifier` protocol
- `AIRequestIntentClassifier`
- `IntelligentRequestRouter`

The intended design preserves explicit command precedence and keeps classification advisory.

Ordinary-language classifications include:

- `conversation`
- `question`
- `task`
- `tool`

The classifier does not execute tools and does not grant authorization.

The original integration target is:

`natural language → route → task/tool task → existing planner → validator → policy → executor → capability`

without moving tool-specific knowledge into `jarvis.py`.

## 13. Original roadmap / preserved planning context

The project originally organized its broader direction as M1–M16. The current M19–M22 verification ledger above is authoritative for the present repository state; the following roadmap is preserved as historical design intent and long-term product philosophy, not as a substitute for the current milestone ledger.

### Goal 1 — Driveable JARVIS / Third Hand

#### M1 — Capability Selection + Invocation

Catalog, selector, selection service, tool bridge, argument proposal, and deterministic invocation validation.

#### M2 — Natural-Language Task Routing

`ask() → intelligent router → TaskRequest → planner → validator → policy → executor`

#### M3 — Multi-Step Agent Execution

Move toward an observe/act loop:

`goal → plan → step → observe → next step → ... → goal achieved`

#### M4 — Capability Discovery

JARVIS understands its currently registered capabilities dynamically rather than through hard-coded lists.

#### M5 — Persistent Working Context

Combine long-term memory, conversation state, current task/goal, workspace state, tool observations, and recent history into coherent working context.

#### M6 — Usable JARVIS Runtime

CLI/runtime first, polished GUI later. The runtime should expose conversation, tasks, execution, confirmation, memory, capability status, and useful logs.

#### M7 — Self-Inspection

JARVIS can inspect its own source, tests, architecture, configuration, runtime state, and capabilities using the same capability system rather than special bypasses.

#### M8 — Safe Self-Modification + Verification

Driveable threshold:

`inspect → identify change → plan modification → confirmation if required → modify → run tests → inspect results → correct/report`

### Goal 2 — “THIS IS JARVIS” / Second Brain

#### M9 — Goal-Oriented Autonomy

Shift from exact instructions toward outcome-oriented goals.

#### M10 — Persistent Projects

Track ongoing projects, tasks, goals, decisions, artifacts, dependencies, experiments, and history across time.

#### M11 — Deep Second-Brain Memory

Connect people, projects, ideas, skills, experiences, decisions, preferences, goals, failures, and lessons rather than acting as a simple fact store.

#### M12 — Broad Plugin / Capability Ecosystem

Expand across GitHub, browser, shell, documents, research, databases, Home Assistant, PCVUE, automation, and other integrations.

#### M13 — Self-Evaluation

Evaluate whether a goal was actually achieved, whether assumptions were wrong, what failed, and what should change.

#### M14 — Self-Improvement

Closed loop:

`observe → identify weakness → propose improvement → modify → test → evaluate`

#### M15 — Initiative

Notice recurring manual work, bottlenecks, opportunities, and relevant context and bring useful suggestions without silently taking unauthorized actions.

#### M16 — THIS IS JARVIS

JARVIS genuinely feels like a personal intelligence system because it understands the user, remembers the user and work, understands projects, knows its capabilities, reasons about goals, acts, inspects itself, modifies itself safely, verifies its work, helps proactively, and improves over time.

## 14. Self-work target architecture

The eventual self-development loop should look like:

```text
User goal
↓
Understand
↓
Discover capabilities
↓
Inspect current state
↓
Reason / plan
↓
Propose actions
↓
Validate
↓
Policy / confirmation
↓
Execute
↓
Run tests / observe
↓
Evaluate
↓
Correct if needed
↓
Report
```

The model is never the final authority over execution.

## 15. Design rules for future development

Before adding a feature, ask:

**Does this make JARVIS a better partner for the user?**

Avoid building things merely because they are technically interesting.

Prefer existing reliable mechanisms over reinventing infrastructure.

Prefer explicit contracts over magic behavior.

Prefer composition over special cases.

Prefer a small core with extensible capabilities over a monolithic agent.

Never sacrifice safety boundaries for convenience.

Do not optimize for flashy autonomy before the underlying system can explain, test, and verify what it is doing.

## 16. Cross-chat session protocol

Every GitHub engineering session begins by reading this file from the current working branch/ref.

Before moving to the next milestone:

1. update this file with the newest verified receipt;
2. record the implementation state of the next milestone;
3. state the active architectural boundary;
4. preserve unresolved issues and known constraints;
5. derive the next milestone from the live repository rather than memory.

A future chat should be able to begin with:

1. Read `docs/JARVIS_MASTER_CONTEXT.md`.
2. Inspect current branch and git status.
3. Run/inspect the relevant tests.
4. Continue from the stated next milestone.

## 17. Verification rule

A milestone is not considered **GREEN / VERIFIED / COMPLETE** until the user provides the local test receipt.

Remote implementation status and local verification status must remain distinct.

No merge is performed unless the user explicitly requests it.

## 18. Current snapshot

**Project:** JARVIS

**Identity:** Third Hand + Second Brain

**Current milestone:** M22.19 Learning Write Execution Boundary — VERIFIED / COMPLETE

**Current branch:** `feature/m22.19-learning-write-execution-boundary`

**Latest verified test suite:** 514/514 for M22.19 (12 focused + 502 core regression)

**Learning pipeline:**

`Execution Feedback → Learning Candidate → Learning Decision → Learning Write Proposal → Learning Write Admission → Learning Write Execution → Learning State / Memory`

**Next milestone:** derive from the live repository after M22.19 verification; do not guess it from memory.
