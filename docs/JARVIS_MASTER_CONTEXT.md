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
Future Adaptation Execution Preparation
↓
Future Adaptation Execution
↓
Future Adaptation Execution Result Integrity
↓
Future Adaptation Execution Result Integrity Feedback
```

The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, preparation, execution, result integrity, and feedback/evaluation.

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
`feature/m22.44-adaptation-evaluation-execution-feedback-result-integrity-feedback`

Latest verified local receipts:
- **M22.43:** 13/13 focused + 502/502 core regression = **515/515**
- **M22.42:** 14/14 focused + 502/502 core regression = **516/516**
- **M22.41:** 14/14 focused + 502/502 core regression = **516/516**
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
M22.1–M22.43 — VERIFIED / COMPLETE.

M22.39 Future Adaptation Execution Feedback → Proposal — VERIFIED / COMPLETE (15/15 focused + 502/502 core = 517/517).
M22.40 Future Adaptation Execution Feedback Proposal → Admission — VERIFIED / COMPLETE (14/14 focused + 502/502 core = 516/516).
M22.41 Future Adaptation Execution Feedback Proposal Admission → Preparation — VERIFIED / COMPLETE (14/14 focused + 502/502 core = 516/516).
M22.42 Future Adaptation Execution Feedback Preparation → Execution — VERIFIED / COMPLETE (14/14 focused + 502/502 core = 516/516).
M22.43 Future Adaptation Execution Feedback Execution → Result Integrity — VERIFIED / COMPLETE (13/13 focused + 502/502 core = 515/515).

**M22.44 Future Adaptation Execution Feedback Result Integrity → Feedback — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT.**

## 7. M22 learning/adaptation architecture and authority walls

M22.34 executes exactly one preparation artifact through a replaceable applier. M22.35 validates execution results. M22.36 converts outcomes into feedback. M22.37 evaluates feedback. M22.38 creates an explicit non-authorizing decision. M22.39 creates an inert proposal. M22.40 admits or rejects that proposal under deterministic policy without granting execution authority. M22.41 converts the exact admitted proposal into immutable execution-preparation state without starting execution. M22.42 performs the future execution attempt through a replaceable applier. M22.43 validates the exact M22.42 result and produces immutable result-integrity evidence. M22.44 converts that integrity evidence into immutable feedback.

### M22.40 — Proposal → Admission
`LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService` consumes one exact M22.39 proposal and validates complete known lineage, bounded confidence, non-empty payload/evidence/provenance, and provider output identity. It produces immutable `ADMITTED` / `REJECTED` policy evidence with a deterministic admission identity. The result remains non-authorizing.

### M22.41 — Admission → Preparation
`LearningWriteAdaptationEvaluationExecutionFeedbackPreparationService` consumes exactly one M22.39 proposal and its exact M22.40 admission. Only `ADMITTED` admissions may cross preparation. The preparation artifact preserves the complete known future-execution lineage, including M22.40 admission identity, M22.39 proposal identity, M22.37 evaluation identity, historical evaluation identity, feedback/source-feedback, candidate/source-candidate, current execution identity, historical source execution, source admission, source proposal, domain, source policy, admission policy, payload, evidence, and provenance.

Payload, evidence, and provenance are recursively frozen. Preparation identity is deterministic and distinct from upstream identities.

Preparation is inert handoff state. It cannot authorize or start execution, request retry, request revocation, mutate memory, or grant general authority.

### M22.42 — Preparation → Execution
`LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService` consumes exactly one M22.41 preparation artifact and builds an immutable execution request. The request preserves the complete M22.41 lineage, including decision/evaluation lineage, execution source, source execution, source admission, source proposal, source policy, admission policy, payload, evidence, and provenance.

Execution uses a replaceable applier. A successful applier call produces an immutable `COMPLETED` result; an applier exception becomes an immutable `FAILED` result with a non-empty reason. Execution receives a deterministic identity distinct from the preparation identity and historical execution-source identity.

Execution remains observational and non-authorizing. It cannot create authorization, retry, revocation, memory mutation, or general authority. Result integrity remains a downstream boundary.

### M22.43 — Execution → Result Integrity
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityService` consumes exactly one M22.42 execution result and its exact execution request. It validates every available lineage identity before normalization, including execution, preparation, admission, proposal, decision, M22.37 evaluation identity, historical evaluation identity, feedback/source-feedback, candidate/source-candidate, execution source, historical source execution, source admission, source proposal, domain, source policy, and admission policy identity.

A `COMPLETED` result becomes immutable `SUCCEEDED` evidence with a deterministic SHA-256 fingerprint of the observed execution result. A `FAILED` result becomes immutable `FAILED` evidence requiring a non-empty failure reason and no fingerprint.

The normalized outcome recursively freezes the observed execution-result payload. Result integrity is evidence about the observed execution result, not proof of adaptation truth, authorization, retry permission, revocation, or memory mutation.

### M22.44 — Result Integrity → Feedback
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService` consumes exactly one M22.43 `LearningWriteAdaptationEvaluationExecutionFeedbackOutcome` and converts its `SUCCEEDED` / `FAILED` status into immutable feedback evidence.

The feedback preserves the complete known M22.43 lineage and preserves the observed execution result, deterministic result fingerprint, or failure reason. Payload and provenance are recursively frozen, and the feedback identity is deterministic and distinct from the source outcome/execution identity.

Feedback remains observational. It does not prove adaptation truth, authorize execution, request execution, request retry, request revocation, mutate memory, or grant general authority.

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
- Execution ≠ Result Integrity
- Result Integrity ≠ Authorization
- Result Integrity ≠ Retry
- Result Integrity ≠ Revocation
- Result Integrity ≠ Memory Mutation
- Feedback ≠ Adaptation Truth
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

**Current milestone:** M22.44 Future Adaptation Execution Feedback Result Integrity → Feedback — ACTIVE / IMPLEMENTED / AWAITING LOCAL RECEIPT.

**Current branch:** `feature/m22.44-adaptation-evaluation-execution-feedback-result-integrity-feedback`

**Latest verified milestone:** M22.43 — 515/515 (13 focused + 502 core regression)

**Active boundary:** Future Adaptation Execution Feedback Result Integrity → Future Adaptation Execution Feedback.

**M22.44 source artifact:** `LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback` from `src/tools/learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback.py`.

**M22.44 service:** `LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService`.

**M22.43 verified receipt:** 13/13 focused + 502/502 core = 515/515.

**M22.44 implementation status:** implemented on PR #187; local verification pending. No merge performed.

**Next action:** run the M22.44 focused suite and core regression locally. Do not merge.
