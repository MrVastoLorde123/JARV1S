# JARVIS Master Context

> Canonical cross-chat continuity document for the JARVIS project. Read this file first at the start of every engineering session, then inspect the current branch/repository state. Repository code/tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's **Third-Hand + Second-Brain**: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning. It is not defined by one LLM, provider, interface, worker, or plugin. Its purpose is to help the user create products and innovations, turn thoughts into words and words into the future, and eventually understand intent so well that explicit instructions become less necessary.

Core loop:
`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Third Hand = action/execution/automation/inspection/modification/verification.
Second Brain = memory/relationships/projects/self-evaluation/initiative/compounding context.

## 2. Core architectural invariants

- Everything is a capability/plugin.
- Scraping and automation are backbone capabilities.
- JARVIS core orchestrates; capabilities implement.
- Model intelligence is advisory; deterministic boundaries retain execution authority.
- Safety is structural, not prompt-only.
- Prefer explicit contracts, composition, small cores, reliable existing mechanisms, and local-first operation.

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
Adaptation Execution
↓
Adaptation Outcome / Result Integrity
↓
Adaptation Feedback
↓
Adaptation Feedback Evaluation
↓
Adaptation Evaluation Decision
↓
Adaptation Evaluation Proposal
↓
Future Adaptation Proposal / Admission
↓
Learning State / Memory Mutation
```

The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, and result integrity.

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

Learning is multi-form: episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning.

## 4. Repository

GitHub: `https://github.com/MrVastoLorde123/JARV1S.git`

Real local project directory:
`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion was a workflow mistake and is considered resolved. Do not resurrect it without new evidence.

## 5. Current verified state

Current milestone branch:
`feature/m22.31-adaptation-evaluation-proposal`

Latest verified local receipts:
- **M22.30:** 12/12 focused + 502/502 core regression = **514/514**
- **M22.29:** 11/11 focused + 502/502 core regression = **513/513**
- **M22.28:** 13/13 focused + 502/502 core regression = **515/515**
- **M22.27:** 13/13 focused + 502/502 core regression = **515/515**
- **M22.26:** 11/11 focused + 502/502 core regression = **513/513**

Previous verified checkpoints:
- M22.25: 11/11 focused + 502/502 core = 513/513
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

## 6. Milestone state

M19 and M20 — VERIFIED / COMPLETE.
M21.1–M21.6 — VERIFIED / COMPLETE.
M22.1–M22.30 — VERIFIED / COMPLETE.

M22.1 Capability / Plugin Contract + Registry — VERIFIED / COMPLETE.
M22.2 Trust / Provenance — VERIFIED / COMPLETE.
M22.3 Lifecycle / Versioning — VERIFIED / COMPLETE.
M22.4 Permission / Policy Binding — VERIFIED / COMPLETE.
M22.5 Plugin Isolation / Execution Sandbox — VERIFIED / COMPLETE (538/538).
M22.6 Capability Discovery + Selection — VERIFIED / COMPLETE (8/8 + 495/495).
M22.7 Capability Proposal → Validated ToolRequest — VERIFIED / COMPLETE.
M22.8 Explicit Authorization — VERIFIED / COMPLETE.
M22.9 Authorization Integrity — VERIFIED / COMPLETE (544/544).
M22.10 Sandbox Admission Integration — VERIFIED / COMPLETE (558/558).
M22.11 Execution Preparation / Handoff — VERIFIED / COMPLETE (571/571).
M22.12 Execution Attempt / Worker — VERIFIED / COMPLETE (583/583).
M22.13 Execution Outcome / Result Integrity — VERIFIED / COMPLETE (514/514).
M22.14 Execution Outcome → Feedback — VERIFIED / COMPLETE (512/512).
M22.15 Feedback Evaluation / Learning Candidate — VERIFIED / COMPLETE (511/511).
M22.16 Learning Decision — VERIFIED / COMPLETE (512/512).
M22.17 Learning Write Proposal — VERIFIED / COMPLETE (515/515).
M22.18 Learning Write Admission — VERIFIED / COMPLETE (514/514).
M22.19 Learning Write Execution — VERIFIED / COMPLETE (514/514).
M22.20 Learning Write Outcome / Result Integrity — VERIFIED / COMPLETE (517/517).
M22.21 Learning Write Outcome → Feedback — VERIFIED / COMPLETE (512/512).
M22.22 Learning Write Feedback → Adaptation Evaluation — VERIFIED / COMPLETE (513/513).
M22.23 Learning Write Adaptation Decision — VERIFIED / COMPLETE (513/513).
M22.24 Adaptation Proposal — VERIFIED / COMPLETE (513/513).
M22.25 Adaptation Proposal → Admission — VERIFIED / COMPLETE (513/513).
M22.26 Adaptation Execution — VERIFIED / COMPLETE (513/513).
M22.27 Adaptation Execution Outcome / Result Integrity — VERIFIED / COMPLETE (515/515).
M22.28 Adaptation Outcome → Feedback — VERIFIED / COMPLETE (515/515).
M22.29 Adaptation Feedback → Evaluation — VERIFIED / COMPLETE (513/513).
M22.30 Adaptation Evaluation → Decision — VERIFIED / COMPLETE (514/514).
**M22.31 Adaptation Evaluation → Proposal — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT.**

## 7. M22 learning/adaptation architecture and authority walls

M22.15–M22.21 establish inert learning-write candidate, decision, proposal, admission, execution, normalized outcome, and feedback boundaries. Observations are evidence, not unquestionable truth.

M22.22 converts learning-write feedback into an immutable adaptation candidate. M22.23 makes an explicit adaptation decision. M22.24 creates an inert adaptation proposal. M22.25 admits/rejects it before execution. M22.26 executes only admitted proposals. M22.27 normalizes execution results and fingerprints successful results. M22.28 converts outcome into inert feedback. M22.29 converts adaptation feedback into immutable evaluation evidence. M22.30 converts that evaluation into a non-authorizing decision.

### M22.31 — Adaptation Evaluation → Proposal
`LearningWriteAdaptationEvaluationProposalService` converts only an accepted adaptation-evaluation decision plus a non-empty proposal payload into an immutable downstream proposal. Deferred or rejected decisions produce no proposal. Proposal, evidence, and provenance are recursively frozen, confidence remains bounded to `[0.0, 1.0]`, deterministic proposal IDs are generated, and exact evaluation/feedback/source-feedback/adaptation-candidate/source-candidate/execution/admission/proposal/domain lineage is preserved.

M22.31 is an explicit inert proposal boundary. It prepares downstream admission; it does not admit, authorize, execute, retry, revoke, or mutate memory.

Walls:
- Adaptation Execution Result ≠ Adaptation Outcome
- Adaptation Outcome ≠ Adaptation Feedback
- Adaptation Feedback ≠ Adaptation Evaluation
- Adaptation Evaluation ≠ Adaptation Evaluation Decision
- Adaptation Evaluation Decision ≠ Adaptation Evaluation Proposal
- Proposal ≠ Admission
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Proposal ≠ Retry Authorization
- Proposal ≠ Revocation
- Proposal ≠ Memory Mutation
- Adaptation Evaluation ≠ Adaptation Truth
- Result Fingerprint ≠ Truth
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## 8. Existing memory decision/write architecture

The memory system separates decision from mutation. `MemoryDecisionProvider` is provider-neutral/non-mutating; `MemoryDecisionService` selects and validates decisions; `MemoryDecisionExecutor` is the mutation boundary for CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE.

Learning/adaptation must not bypass this architecture. Any future mapping from adaptation to memory must cross the established memory decision/executor contract.

Memory taxonomy:
`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

## 9. Capability/plugin ecosystem foundation

Capability contract/registry, trust/provenance, lifecycle/versioning, permission/policy binding, sandbox, discovery/selection, proposal/invocation, authorization/integrity, execution preparation, execution attempt, outcome, and feedback are explicit boundaries.

Capability execution path:
`proposal → validation → policy → confirmation → authorization → authorization integrity → sandbox admission → execution preparation → execution attempt → outcome → feedback`

## 10. Workspace capability — frozen

Capabilities: `read_file`, `list_directory`, `search_files`, `write_file`.
Read/list/search are low-risk and read-only. `write_file` is high-risk and confirmation-gated.

## 11. Tool capability bridge — completed foundation

Core defines `ToolInvoker`, `ToolCapabilityGateway`, and `ToolPlanStepHandler`.
Representative flow:
`JARVIS → TaskRequest → ExecutionPlanner → PlanValidator → ExecutionPolicy → PlanExecutor → ToolPlanStepHandler → ToolInvoker → PolicyGate → ToolService → ToolHandler`

## 12. Natural-language routing groundwork

Routing includes `RequestIntent`, `RequestIntentClassifier`, `AIRequestIntentClassifier`, and `IntelligentRequestRouter`. Classification is advisory and does not execute tools or grant authorization.

Target integration:
`natural language → route → task/tool task → existing planner → validator → policy → executor → capability`

## 13. Original roadmap / preserved planning context

The original M1–M16 roadmap remains historical design intent; the current M19–M22 verification ledger is authoritative for repository state.

Goal 1 — Driveable JARVIS / Third Hand:
M1 Capability Selection + Invocation; M2 Natural-Language Task Routing; M3 Multi-Step Agent Execution; M4 Capability Discovery; M5 Persistent Working Context; M6 Usable JARVIS Runtime; M7 Self-Inspection; M8 Safe Self-Modification + Verification.

Goal 2 — THIS IS JARVIS / Second Brain:
M9 Goal-Oriented Autonomy; M10 Persistent Projects; M11 Deep Second-Brain Memory; M12 Broad Plugin / Capability Ecosystem; M13 Self-Evaluation; M14 Self-Improvement; M15 Initiative; M16 THIS IS JARVIS.

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

## 15. Design rules

Before adding a feature ask: **Does this make JARVIS a better partner for the user?**

Prefer explicit contracts, composition, deterministic boundaries, reliable existing mechanisms, local-first operation, and safety over convenience. Do not optimize for flashy autonomy before the system can explain, test, and verify what it is doing.

## 16. Cross-chat session protocol

Every GitHub engineering session begins by reading this file from the current working branch/ref.

Before moving to the next milestone:
1. update this file with the newest verified receipt;
2. record the implementation state of the next milestone;
3. state the active architectural boundary;
4. preserve unresolved issues and known constraints;
5. derive the next milestone from the live repository rather than memory.

## 17. Verification rule

A milestone is not **GREEN / VERIFIED / COMPLETE** until the user provides the local test receipt.

Remote implementation status and local verification status remain distinct.

No merge is performed unless explicitly requested.

## 18. Current snapshot

**Project:** JARVIS

**Identity:** Third Hand + Second Brain

**Current milestone:** M22.31 Adaptation Evaluation → Proposal — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT

**Current branch:** `feature/m22.31-adaptation-evaluation-proposal`

**Latest verified milestone:** M22.30 — 514/514 (12 focused + 502 core regression)

**Learning/adaptation pipeline:**
`Execution Feedback → Learning Candidate → Learning Decision → Learning Write Proposal → Learning Write Admission → Learning Write Execution → Learning Write Outcome → Learning Write Feedback → Adaptation Evaluation → Adaptation Candidate → Adaptation Decision → Adaptation Proposal → Adaptation Admission → Adaptation Execution → Adaptation Outcome / Result Integrity → Adaptation Feedback → Adaptation Feedback Evaluation → Adaptation Evaluation Decision → Adaptation Evaluation Proposal → Future Adaptation Proposal / Admission → Learning State / Memory`

**Next milestone:** derive from the live repository after M22.31 verification; do not guess it from memory.
