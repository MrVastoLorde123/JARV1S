# JARVIS Master Context

> Canonical cross-chat continuity document for the JARVIS project.
> This is the single source-of-truth context document. Read it first at the start of every engineering session, then inspect the current branch/repository state. Repository code and tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's **Third-Hand + Second-Brain**: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning.

It is not defined by one LLM, model, provider, interface, worker, or plugin. It is not primarily a product to sell. Its purpose is to help the user create products and innovations, turn thoughts into words and words into the future, and eventually understand intent so well that explicit instructions become less necessary.

Core long-term loop:
`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Two complementary halves:
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

### Execution authority chain
`Reasoning → Interpretation → Prioritization → Proposal → Validation → Policy → Confirmation → Confirmation Integrity → Authorization → Authorization Integrity → Sandbox Admission → Execution Preparation/Handoff → Execution Attempt → Outcome`

### Learning/adaptation chain
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
Learning Write Outcome
↓
Learning Write Feedback
↓
Learning/Adaptation Evaluation
↓
Adaptation Candidate
↓
Adaptation Decision
↓
Adaptation Proposal
↓
Adaptation Admission
↓
Future Adaptation Execution
↓
Learning State / Memory Mutation
```

The final write/mutation boundary remains downstream from evidence, reasoning, decisions, proposals, and policy.

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

Real local project directory:
`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion was a workflow mistake and is considered resolved. Do not resurrect that issue without new evidence.

## 5. Current verified state

Current milestone branch:
`feature/m22.25-adaptation-proposal-admission`

Latest verified local receipt:
- **M22.25:** 11/11 focused + 502/502 core regression = **513/513**

Previous verified checkpoints:
- M22.24: 11/11 focused + 502/502 core = 513/513
- M22.23: 11/11 focused + 502/502 core = 513/513
- M22.22: 11/11 focused + 502/502 core = 513/513
- M22.21: 10/10 focused + 502/502 core = 512/512
- M22.20: 15/15 focused + 502/502 core = 517/517
- M22.19: 12/12 focused + 502/502 core = 514/514
- M22.18: 12/12 focused + 502/502 core = 514/514
- M22.17: 13/13 focused + 502/502 core = 515/515
- M22.16: 10/10 focused + 502/502 core = 512/512
- M22.15: 9/9 focused + 502/502 core = 511/511
- M22.14: 10/10 focused + 502/502 core = 512/512
- M22.13: 12/12 focused + 502/502 core = 514/514
- M22.12: 583/583 cumulative coverage
- M22.11: 571/571
- M22.10: 558/558
- M22.9: 544/544
- M22.8: focused authorization/gate/legacy coverage + 502/502 core
- M22.7: 502/502 core regression with focused capability-request coverage

M19 and M20 are VERIFIED / COMPLETE. M21.1 through M21.6 are VERIFIED / COMPLETE according to the milestone history.

## 6. Milestone state

- M19 Deep Personalization — VERIFIED / COMPLETE
- M20 Long-Horizon Task Management — VERIFIED / COMPLETE
- M21.1 Proactive Initiative Boundary — VERIFIED / COMPLETE
- M21.2 Proactive Proposal Boundary — VERIFIED / COMPLETE
- M21.3 Proactive Value Assessment — VERIFIED / COMPLETE
- M21.4 Information Gain / Uncertainty Reduction — VERIFIED / COMPLETE
- M21.5 Bounded Proactive Scheduling / Notification — VERIFIED / COMPLETE
- M21.6 Proactive Runtime / Feedback Integration — VERIFIED / COMPLETE
- M22 Capability / Plugin Ecosystem — ACTIVE
- M22.1 Capability / Plugin Contract + Registry Boundary — VERIFIED / COMPLETE
- M22.2 Capability Trust / Provenance Boundary — VERIFIED / COMPLETE
- M22.3 Capability Lifecycle / Versioning Boundary — VERIFIED / COMPLETE
- M22.4 Capability Permission / Policy Binding — VERIFIED / COMPLETE
- M22.5 Plugin Isolation / Execution Sandbox — VERIFIED / COMPLETE (538/538)
- M22.6 Capability Discovery + Selection Integration — VERIFIED / COMPLETE (8/8 focused + 495/495 core)
- M22.7 Capability Proposal → Validated ToolRequest Boundary — VERIFIED / COMPLETE (502/502 core)
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
- M22.20 Learning Write Outcome / Result Integrity Boundary — VERIFIED / COMPLETE (517/517)
- M22.21 Learning Write Outcome → Feedback Boundary — VERIFIED / COMPLETE (512/512)
- M22.22 Learning Write Feedback → Adaptation Evaluation Boundary — VERIFIED / COMPLETE (513/513)
- M22.23 Learning Write Adaptation Decision Boundary — VERIFIED / COMPLETE (513/513)
- M22.24 Adaptation Proposal Boundary — VERIFIED / COMPLETE (513/513)
- M22.25 Adaptation Proposal → Admission Boundary — VERIFIED / COMPLETE (513/513)

## 7. M22 learning/adaptation architecture and authority walls

### M22.15 — Learning Candidate
`FeedbackEvaluationService` converts inert execution feedback into an immutable `LearningCandidate` carrying signal classification, confidence, evidence, and provenance. It does not write learning, mutate memory, re-authorize, retry, revoke, or execute.

### M22.16 — Learning Decision
`LearningDecisionService` consumes a `LearningCandidate` and produces an immutable `LearningDecision` with explicit `ACCEPT`, `DEFER`, or `REJECT` semantics. The decision remains non-writing and non-authorizing.

### M22.17 — Learning Write Proposal
`LearningWriteProposalService` converts only an `ACCEPT` decision into an inert, immutable `LearningWriteProposal`. It carries explicit domain/payload/evidence/provenance and exact lineage but cannot authorize, execute, retry, revoke, or mutate memory.

### M22.18 — Learning Write Admission
`LearningWriteAdmissionService` evaluates proposal structure and policy conditions before mutation. Baseline requires non-empty payload, evidence, provenance, and confidence >= 0.5. It returns `ADMITTED` or `REJECTED` and remains non-writing/non-authorizing.

### M22.19 — Learning Write Execution
`LearningWriteExecutionService` is the controlled write-execution boundary after admission. Only an `ADMITTED` proposal can execute through a replaceable `LearningWriter`; failures become explicit immutable results. It does not grant execution authority, bypass sandbox, retry, revoke, or define concrete persistent stores.

### M22.20 — Learning Write Outcome / Result Integrity
`LearningWriteOutcomeService` interprets a `LearningWriteExecutionResult` against the exact request that produced it, verifies identity lineage, normalizes success/failure, and fingerprints successful writer results. Outcome is evidence, not truth.

### M22.21 — Learning Write Outcome → Feedback
`LearningWriteFeedbackService` converts a verified outcome into an immutable `LearningWriteFeedbackEvent`, preserving exact identity/provenance and recursively freezing snapshots. It is inert and does not evaluate correctness, mutate state, authorize, retry, revoke, or execute.

### M22.22 — Learning Write Feedback → Adaptation Evaluation
`LearningWriteFeedbackEvaluationService` converts learning-write feedback into an immutable `LearningWriteAdaptationCandidate`. Success and failure become explicit adaptation signals. Lineage, evidence, provenance, and deterministic identity are preserved. Evaluation is non-writing and non-authorizing.

### M22.23 — Learning Write Adaptation Decision
`LearningWriteAdaptationDecisionService` converts an adaptation candidate into an immutable `LearningWriteAdaptationDecision` with explicit `ACCEPT`, `DEFER`, or `REJECT`. The deterministic baseline accepts successful write signals and defers failed write signals. The decision cannot grant adaptation-write, memory-mutation, authorization, retry, or revocation authority.

### M22.24 — Adaptation Proposal
`LearningWriteAdaptationProposalService` converts only an `ACCEPT` adaptation decision plus its exact source adaptation candidate into an immutable `LearningWriteAdaptationProposal`. It preserves feedback, execution, admission, learning-write proposal, decision, source-candidate, and domain lineage, recursively freezes adaptation/evidence/provenance, and derives deterministic proposal identity.

M22.24 is deliberately inert. It does not apply adaptations, mutate learning or memory, authorize execution, retry, revoke, or define adaptation persistence/execution infrastructure.

M22.24 walls:
- Adaptation Decision ≠ Adaptation Proposal
- Adaptation Proposal ≠ Adaptation Admission
- Adaptation Proposal ≠ Memory Mutation
- Adaptation Proposal ≠ Authorization
- Adaptation Proposal ≠ Retry Authorization
- Adaptation Proposal ≠ Revocation
- Evaluation ≠ Authority
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

### M22.25 — Adaptation Proposal → Admission
`LearningWriteAdaptationAdmissionService` evaluates an adaptation proposal before any future adaptation execution path can consume it. The admission result is immutable and identity-bound. The deterministic baseline requires non-empty adaptation, evidence, provenance, and confidence >= 0.5, returning `ADMITTED` or `REJECTED`.

M22.25 is deliberately non-executing. Admission does not apply an adaptation, mutate learning or memory, authorize tools, retry, revoke, or establish adaptation truth.

M22.25 walls:
- Adaptation Proposal ≠ Adaptation Admission
- Adaptation Admission ≠ Adaptation Execution
- Adaptation Admission ≠ Memory Mutation
- Adaptation Admission ≠ Authorization
- Adaptation Admission ≠ Retry Authorization
- Adaptation Admission ≠ Revocation
- Admission ≠ Truth
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## 8. Existing memory decision/write architecture

The memory system already separates decision from mutation. `MemoryDecisionProvider` is provider-neutral and non-mutating; `MemoryDecisionService` selects and validates decisions; `MemoryDecisionExecutor` is the mutation boundary for CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE.

Learning/adaptation must not bypass this architecture. Any future mapping from adaptation to memory must cross the established memory decision/executor contract.

Memory taxonomy:
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## 9. Capability/plugin ecosystem foundation

Capability contracts, registry, trust/provenance, lifecycle/versioning, permission/policy binding, sandbox, discovery/selection, proposal/invocation, authorization/integrity, execution preparation, execution attempt, outcome, and feedback are all explicit boundaries. Registration/discovery/trust/selection do not grant execution authority.

Capability execution path:
`proposal → validation → policy → confirmation → authorization → authorization integrity → sandbox admission → execution preparation → execution attempt → outcome → feedback`

## 10. Workspace capability — frozen

Capabilities: `read_file`, `list_directory`, `search_files`, `write_file`.
Read/list/search are low-risk and read-only. `write_file` is high-risk and confirmation-gated. Shared behavior covers confinement, relative reporting, traversal rules, hidden entries, symlinks, filesystem-error normalization, and limits.

## 11. Tool capability bridge — completed foundation

Core defines `ToolInvoker`, `ToolCapabilityGateway`, and `ToolPlanStepHandler`.
Representative flow:
`JARVIS → TaskRequest → ExecutionPlanner → PlanValidator → ExecutionPolicy → PlanExecutor → ToolPlanStepHandler → ToolInvoker → PolicyGate → ToolService → ToolHandler`

The model is advisory; capability-specific policy remains at the capability boundary.

## 12. Natural-language routing groundwork

Routing groundwork includes `RequestIntent`, `RequestIntentClassifier`, `AIRequestIntentClassifier`, and `IntelligentRequestRouter`. Explicit command precedence remains intact and classification does not execute tools or grant authorization.

Target integration:
`natural language → route → task/tool task → existing planner → validator → policy → executor → capability`

## 13. Original roadmap / preserved planning context

The original long-term organization was M1–M16. The current M19–M22 verification ledger above is authoritative for repository state; this roadmap remains historical design intent and product philosophy.

### Goal 1 — Driveable JARVIS / Third Hand
- **M1 — Capability Selection + Invocation:** catalog, selector, selection service, tool bridge, argument proposal, deterministic invocation validation.
- **M2 — Natural-Language Task Routing:** `ask() → intelligent router → TaskRequest → planner → validator → policy → executor`.
- **M3 — Multi-Step Agent Execution:** `goal → plan → step → observe → next step → ... → goal achieved`.
- **M4 — Capability Discovery:** dynamically understand registered capabilities.
- **M5 — Persistent Working Context:** combine memory, conversation, current task/goal, workspace state, observations, and recent history.
- **M6 — Usable JARVIS Runtime:** CLI/runtime first, polished GUI later.
- **M7 — Self-Inspection:** inspect source, tests, architecture, configuration, runtime state, and capabilities using the same capability system.
- **M8 — Safe Self-Modification + Verification:** `inspect → identify change → plan modification → confirmation if required → modify → run tests → inspect results → correct/report`.

### Goal 2 — THIS IS JARVIS / Second Brain
- **M9 — Goal-Oriented Autonomy:** shift toward outcome-oriented goals.
- **M10 — Persistent Projects:** track tasks, goals, decisions, artifacts, dependencies, experiments, and history.
- **M11 — Deep Second-Brain Memory:** connect people, projects, ideas, skills, experiences, decisions, preferences, goals, failures, and lessons.
- **M12 — Broad Plugin / Capability Ecosystem:** expand across GitHub, browser, shell, documents, research, databases, Home Assistant, PCVUE, automation, and other integrations.
- **M13 — Self-Evaluation:** evaluate goal achievement, assumptions, failure, and needed change.
- **M14 — Self-Improvement:** `observe → identify weakness → propose improvement → modify → test → evaluate`.
- **M15 — Initiative:** notice recurring work, bottlenecks, opportunities, and context without silently taking unauthorized actions.
- **M16 — THIS IS JARVIS:** personal intelligence that understands, remembers, reasons, acts, inspects itself, modifies safely, verifies work, helps proactively, and improves.

## 14. Self-work target architecture

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

The model is never final authority over execution.

## 15. Design rules for future development

Before adding a feature, ask: **Does this make JARVIS a better partner for the user?**

Avoid building things merely because they are technically interesting. Prefer explicit contracts, composition, small deterministic boundaries, reliable existing mechanisms, and safety over convenience. Do not optimize for flashy autonomy before the system can explain, test, and verify what it is doing.

## 16. Cross-chat session protocol

Every GitHub engineering session begins by reading this file from the current working branch/ref.

Before moving to the next milestone:
1. update this file with the newest verified receipt;
2. record the implementation state of the next milestone;
3. state the active architectural boundary;
4. preserve unresolved issues and known constraints;
5. derive the next milestone from the live repository rather than memory.

Future chats should be able to begin with:
1. Read `docs/JARVIS_MASTER_CONTEXT.md`.
2. Inspect current branch and git status.
3. Run/inspect relevant tests.
4. Continue from the stated next milestone.

## 17. Verification rule

A milestone is not **GREEN / VERIFIED / COMPLETE** until the user provides the local test receipt.

Remote implementation status and local verification status must remain distinct.

No merge is performed unless the user explicitly requests it.

## 18. Current snapshot

**Project:** JARVIS

**Identity:** Third Hand + Second Brain

**Current milestone:** M22.25 Adaptation Proposal → Admission Boundary — VERIFIED / COMPLETE

**Current branch:** `feature/m22.25-adaptation-proposal-admission`

**Latest verified milestone:** M22.25 — 513/513 (11 focused + 502 core regression)

**Learning/adaptation pipeline:**
`Execution Feedback → Learning Candidate → Learning Decision → Learning Write Proposal → Learning Write Admission → Learning Write Execution → Learning Write Outcome → Learning Write Feedback → Adaptation Evaluation → Adaptation Candidate → Adaptation Decision → Adaptation Proposal → Adaptation Admission → Future Adaptation Execution → Learning State / Memory`

**Next milestone:** derive from the live repository after M22.25 verification; do not guess it from memory.
