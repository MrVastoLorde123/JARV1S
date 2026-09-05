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
Adaptation Evaluation Proposal Admission
↓
Future Adaptation Execution Preparation
↓
Future Adaptation Execution
↓
Future Adaptation Execution Result / Result Integrity
↓
Future Adaptation Execution Feedback
↓
Future Adaptation Execution Feedback Evaluation
↓
Future Adaptation Execution Feedback Decision
↓
Future Adaptation Execution Feedback Proposal
↓
Future Adaptation Execution Feedback Proposal Admission
↓
Future Adaptation Execution Feedback Preparation
↓
Future Adaptation Execution
```

The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, preparation, execution, and result integrity.

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
`feature/m22.41-adaptation-evaluation-execution-feedback-preparation`

Latest verified local receipts:
- **M22.40:** 14/14 focused + 502/502 core regression = **516/516**
- **M22.39:** 15/15 focused + 502/502 core regression = **517/517**
- **M22.38:** 13/13 focused + 502/502 core regression = **515/515**
- **M22.37:** 12/12 focused + 502/502 core regression = **514/514**
- **M22.36:** 14/14 focused + 502/502 core regression = **516/516**
- **M22.35:** 14/14 focused + 502/502 core regression = **516/516**
- **M22.34:** 13/13 focused + 502/502 core regression = **515/515**

Previous verified checkpoints remain recorded in repository history.

## 6. Milestone state

M19 and M20 — VERIFIED / COMPLETE.
M21.1–M21.6 — VERIFIED / COMPLETE.
M22.1–M22.40 — VERIFIED / COMPLETE.

M22.39 Future Adaptation Execution Feedback → Proposal — VERIFIED / COMPLETE (15/15 focused + 502/502 core = 517/517).
M22.40 Future Adaptation Execution Feedback Proposal → Admission — VERIFIED / COMPLETE (14/14 focused + 502/502 core = 516/516).

**M22.41 Future Adaptation Execution Feedback Proposal Admission → Preparation — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT.**

## 7. M22 learning/adaptation architecture and authority walls

M22.34 executes exactly one preparation artifact through a replaceable applier. M22.35 validates execution results. M22.36 converts outcomes into feedback. M22.37 evaluates feedback. M22.38 creates an explicit non-authorizing decision. M22.39 creates an inert proposal. M22.40 admits or rejects that proposal under deterministic policy without granting execution authority.

### M22.40 — Proposal → Admission
`LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService` consumes one exact M22.39 proposal and one admission context. It validates complete known proposal lineage, bounded confidence, non-empty payload/evidence/provenance, and produces immutable `ADMITTED` / `REJECTED` policy evidence with a deterministic admission identity. The result remains non-authorizing.

### M22.41 — Admission → Preparation
`LearningWriteAdaptationEvaluationExecutionFeedbackPreparationService` consumes exactly one M22.39 proposal and its exact M22.40 admission. Only `ADMITTED` admissions may cross preparation. The preparation artifact preserves the complete known future-execution lineage, including M22.40 admission identity, M22.39 proposal identity, M22.37 evaluation identity, historical evaluation identity, feedback/source-feedback, candidate/source-candidate, execution/source-execution, source admission, source proposal, domain, source policy, admission policy, payload, evidence, and provenance.

Payload, evidence, and provenance are recursively frozen. Preparation identity is deterministic and distinct from upstream identities.

Preparation is inert handoff state. It cannot authorize or start execution, request retry, request revocation, mutate memory, or grant general authority. Downstream future execution remains a separate boundary.

Walls:
- Execution ≠ Result Integrity
- Result Integrity ≠ Feedback
- Feedback ≠ Feedback Evaluation
- Feedback Evaluation ≠ Feedback Evaluation Decision
- Decision ≠ Proposal
- Proposal ≠ Admission
- Admission ≠ Preparation
- Preparation ≠ Authorization
- Preparation ≠ Execution
- Preparation ≠ Retry
- Preparation ≠ Revocation
- Preparation ≠ Memory Mutation
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

## 12. Natural-language routing groundwork

Routing includes `RequestIntent`, `RequestIntentClassifier`, `AIRequestIntentClassifier`, and `IntelligentRequestRouter`. Classification is advisory and does not execute tools or grant authorization.

## 13. Original roadmap / preserved planning context

The original M1–M16 roadmap remains historical design intent; the current M19–M22 verification ledger is authoritative for repository state.

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

**Current milestone:** M22.41 Future Adaptation Execution Feedback Proposal Admission → Preparation — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT.

**Current branch:** `feature/m22.41-adaptation-evaluation-execution-feedback-preparation`

**Latest verified milestone:** M22.40 — 516/516 (14 focused + 502 core regression)

**Active boundary:** Future Adaptation Execution Feedback Proposal Admission → Future Adaptation Execution Feedback Preparation.

**M22.41 source artifact:** `LearningWriteAdaptationEvaluationExecutionFeedbackPreparation` from `src/tools/learning_write_adaptation_evaluation_execution_feedback_preparation.py`.

**Next action:** run the M22.41 focused suite and core regression locally. After verification, derive M22.42 from the live preparation artifact. Do not merge.
