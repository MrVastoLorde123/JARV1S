# JARVIS Master Context

> Canonical cross-chat continuity document for JARVIS. Read this file first at the start of every engineering session, then inspect the current branch/repository state. Repository code/tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's **Third-Hand + Second-Brain**: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning. It is not defined by one LLM, provider, interface, worker, or plugin.

Core loop:
`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Everything is a capability/plugin. Scraping and automation are backbone capabilities. JARVIS core orchestrates; capabilities implement. Model intelligence is advisory; deterministic boundaries retain execution authority. Safety is structural, not prompt-only. Prefer explicit contracts, composition, small cores, reliable existing mechanisms, and local-first operation.

Non-negotiable separations:
- Intelligence ≠ Authority
- Learning ≠ Authority
- Adaptation ≠ Authorization
- Capability ≠ Permission
- Planning ≠ Execution
- Proposal ≠ Authorization
- Memory ≠ User Intent
- Knowledge ≠ Truth
- Confidence ≠ Certainty
- Prediction ≠ Permission

## 2. Authority chains

Execution:
`Reasoning → Interpretation → Prioritization → Proposal → Validation → Policy → Confirmation → Confirmation Integrity → Authorization → Authorization Integrity → Sandbox Admission → Execution Preparation/Handoff → Execution Attempt → Outcome`

Learning/adaptation:
`Execution Outcome → Execution Feedback → Feedback Evaluation → Learning Candidate → Learning Decision → Learning Write Proposal → Learning Write Admission → Learning Write Execution → Learning Write Outcome → Learning Write Feedback → Learning/Adaptation Evaluation → Adaptation Candidate → Adaptation Decision → Adaptation Proposal → Adaptation Admission → Adaptation Execution → Adaptation Outcome / Result Integrity → Adaptation Feedback → Adaptation Feedback Evaluation → Adaptation Evaluation Decision → Adaptation Evaluation Proposal → Adaptation Evaluation Proposal Admission → Future Adaptation Execution Preparation → Future Adaptation Execution → Future Adaptation Execution Result / Result Integrity → Future Adaptation Execution Feedback → Future Adaptation Execution Feedback Evaluation → Future Adaptation Execution Feedback Decision → Future Adaptation Execution Feedback Proposal → Future Adaptation Execution Feedback Proposal Admission → Future Adaptation Execution Preparation → Future Adaptation Execution → Future Adaptation Execution Result Integrity → Future Adaptation Execution Result Integrity Feedback → Future Adaptation Execution Result Integrity Feedback Evaluation → Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision → Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal → Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal Admission`

The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, preparation, execution, result integrity, feedback, and evaluation.

## 3. Cognitive architecture

`Environment/User → Perception/Input → Evidence+Provenance → Memory+Personal Knowledge → World Model/Current Context → Reasoning+Uncertainty → Initiative Candidate → Initiative Evaluation → Proactive Proposal → Value Assessment → Information Gain/Uncertainty Reduction → Bounded Scheduling/Notification Proposal → Proactive Runtime/Feedback → Capability Discovery/Selection → Prioritization → Validation/Policy → Confirmation → Authorization → Execution/Capabilities → Outcome/Feedback → Learning`

Learning forms include episodic, semantic, procedural, preference, failure/outcome, belief revision, predictive, and meta-learning.

## 4. Repository

GitHub: `https://github.com/MrVastoLorde123/JARV1S.git`

Real local project directory:
`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion was a workflow mistake and is resolved.

## 5. Verified milestone ledger

M19 and M20 — VERIFIED / COMPLETE.
M21.1–M21.6 — VERIFIED / COMPLETE.
M22.1–M22.48 — VERIFIED / COMPLETE.

Recent receipts:
- M22.48: 17/17 focused + 502/502 core = **519/519**
- M22.47: 16/16 focused + 502/502 core = **518/518**
- M22.46: 15/15 focused + 502/502 core = **517/517**
- M22.45: 13/13 focused + 502/502 core = **515/515**
- M22.44: 11/11 focused + 502/502 core = **513/513**
- M22.43: 13/13 focused + 502/502 core = **515/515**
- M22.42: 14/14 focused + 502/502 core = **516/516**

M22.39: 15/15 + 502/502 = 517/517.
M22.40: 14/14 + 502/502 = 516/516.
M22.41: 14/14 + 502/502 = 516/516.
M22.38: 13/13 + 502/502 = 515/515.
M22.37: 12/12 + 502/502 = 514/514.
M22.36: 14/14 + 502/502 = 516/516.
M22.35: 14/14 + 502/502 = 516/516.
M22.34: 13/13 + 502/502 = 515/515.

## 6. Current milestone

**M22.48 Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal → Admission — VERIFIED / COMPLETE.**

Branch:
`feature/m22.48-adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal-admission`

Parent:
`feature/m22.47-adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal`

Parent receipt:
M22.47 = **16/16 focused + 502/502 core = 518/518**.

PR: #191, open and unmerged.

M22.48 receipt:
**17/17 focused + 502/502 core = 519/519, all passing.**

## 7. Recent contracts

### M22.43 — Execution → Result Integrity
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityService` consumes exactly one M22.42 execution result and exact request. It validates full lineage, maps COMPLETED → immutable SUCCEEDED evidence with deterministic SHA-256 fingerprint, maps FAILED → immutable FAILED evidence with required reason and no fingerprint, recursively freezes the observed execution result, and remains observational/non-authorizing.

### M22.44 — Result Integrity → Feedback
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService` consumes exactly one M22.43 integrity outcome. It converts SUCCEEDED/FAILED into immutable feedback evidence, preserves complete known M22.43 lineage, preserves observed execution evidence/fingerprint/failure reason, recursively freezes payload/provenance, derives deterministic feedback identity distinct from source outcome/execution identity, and does not authorize execution, retry, revocation, memory mutation, or adaptation truth.

### M22.45 — Feedback → Evaluation
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService` consumes exactly one M22.44 result-integrity feedback artifact and produces immutable evaluation evidence with deterministic identity, complete lineage, bounded confidence, integrity-success/failure signals, recursive immutability, and no authority.

A namespace collision was discovered during local import verification: the pre-existing M22.37 module `learning_write_adaptation_evaluation_execution_feedback_evaluation.py` is required by the older decision/proposal chain. M22.45 therefore uses the dedicated module `learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation.py` and dedicated class/service names. The M22.37 module remains unchanged.

### M22.46 — Evaluation → Decision
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService` consumes exactly one M22.45 evaluation artifact and produces an immutable explicit decision.

Its dedicated namespace is `src/tools/learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision.py` to avoid collision with the established M22.37 decision namespace.

It preserves the full M22.45 lineage, including the M22.45 evaluation identity, M22.44 feedback identity, historical evaluation identity, outcome/execution/preparation/admission/proposal/decision identities, source feedback/candidate/execution/admission/proposal identities, domain, source policy, and admission policy.

Deterministic baseline:
- integrity-failure signal → `DEFER`;
- confidence below `0.5` → `DEFER`;
- otherwise → `ACCEPT`.

The new decision identity is deterministic and distinct from upstream evaluation, feedback, and execution identities. Returned decisions are provider-neutral and non-authorizing.

M22.46 is verified and remains advisory decision evidence only. It does not authorize execution, request execution, request retry, request revocation, mutate memory, grant authority, or establish adaptation truth.

### M22.47 — Decision → Proposal
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService` consumes exactly one M22.46 decision artifact and produces an immutable proposal only when the decision action is `ACCEPT`. `DEFER` and `REJECT` produce no proposal.

Its dedicated namespace is `src/tools/learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal.py` to preserve namespace integrity established by M22.45/M22.46 and leave M22.37 untouched.

The proposal preserves the full known M22.46 lineage, including the M22.46 decision identity, current evaluation identity, historical evaluation identity, feedback identity, outcome/execution/preparation/admission/proposal/decision identities, source feedback/candidate/execution/admission/proposal identities, domain, source policy, and admission policy.

The new proposal identity is deterministic and distinct from upstream decision/evaluation/feedback/execution identities. Payload, evidence, provenance, and metadata are recursively immutable and confidence is bounded to [0,1].

M22.47 remains non-authorizing. The proposal cannot execute, authorize, request execution, retry, revoke, mutate memory, grant authority, or establish adaptation truth. Admission and downstream preparation/execution remain independent boundaries.

M22.47 is verified and remains proposal evidence only.

### M22.48 — Proposal → Admission
`LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService` consumes exactly one M22.47 proposal artifact and produces one immutable `ADMITTED` or `REJECTED` admission artifact.

The deterministic baseline rejects unsupported proposal kinds, non-accept actions, confidence below `0.5`, and empty payload/evidence/provenance; otherwise it admits. The provider is replaceable while the service validates returned type and full proposal lineage.

The admission preserves M22.47 proposal identity and the full known upstream lineage. `source_policy_id` preserves the M22.47 proposal policy while the new `policy_id` identifies the M22.48 admission policy. `admission_id` is deterministic and distinct from upstream proposal, decision, evaluation, feedback, and execution identities.

Payload/evidence/provenance/metadata are recursively immutable, confidence remains bounded to [0,1], and the admission authority wall hard-fails any attempt to authorize execution, request execution, request retry, revoke, mutate memory, or grant general authority. M22.48 does not establish adaptation truth.

M22.48 uses the dedicated `..._evaluation_decision_proposal_admission.py` namespace; M22.37 remains unchanged.

M22.48 is **VERIFIED / COMPLETE: 17/17 focused + 502/502 core = 519/519**.

## 8. Authority walls

- Execution ≠ Result Integrity
- Result Integrity ≠ Feedback
- Feedback ≠ Feedback Evaluation
- Feedback Evaluation ≠ Feedback Evaluation Decision
- Decision ≠ Proposal
- Proposal ≠ Admission
- Admission ≠ Preparation
- Preparation ≠ Authorization
- Preparation ≠ Execution
- Result Integrity ≠ Authorization
- Result Integrity ≠ Retry
- Result Integrity ≠ Revocation
- Result Integrity ≠ Memory Mutation
- Feedback ≠ Adaptation Truth
- Evaluation ≠ Adaptation Truth
- Evidence ≠ Truth
- Learning ≠ Authority

M22.46 additionally cannot authorize execution, request execution, request retry, request revocation, mutate memory, grant general authority, or establish adaptation truth.

M22.47 additionally cannot execute, authorize, request execution, retry, revoke, mutate memory, grant authority, or establish adaptation truth.

M22.48 additionally cannot authorize execution, request execution, request retry, request revocation, mutate memory, grant general authority, or establish adaptation truth.

## 9. M22.48 contract

M22.48 consumes exactly one M22.47 proposal artifact and produces an immutable admission artifact.

Admission validates the exact proposal type, accepted proposal kind/action, complete known lineage, bounded confidence, and required non-empty payload/evidence/provenance. It emits an explicit `ADMITTED` or `REJECTED` status through a provider-neutral admission interface.

The admission preserves the complete known M22.47 lineage, including proposal identity, upstream M22.46 decision/evaluation identities, feedback/outcome/execution/preparation/admission/proposal identities, source identities, domain, source policy, and proposal/admission policy identities.

Admission receives its own deterministic identity distinct from proposal/decision/evaluation/feedback/execution identities. Confidence remains bounded to [0,1], nested payload/evidence/provenance remain recursively immutable, and provider output identity is validated by the service.

Admission does not authorize execution, request execution, retry, revoke, mutate memory, grant authority, or establish adaptation truth. Preparation and execution remain independent downstream boundaries.

## 10. Memory and capability architecture

Memory separates decision from mutation: `MemoryDecisionProvider` is provider-neutral/non-mutating; `MemoryDecisionService` selects and validates; `MemoryDecisionExecutor` is the mutation boundary for CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE. Adaptation must not bypass this architecture.

Capability ecosystem: contract/registry, trust/provenance, lifecycle/versioning, permission/policy binding, sandbox, discovery/selection, proposal/invocation, authorization/integrity, execution preparation, execution attempt, outcome, and feedback are explicit boundaries.

Workspace capabilities are `read_file`, `list_directory`, `search_files`, and `write_file`; `write_file` is confirmation-gated.

## 11. Self-work target architecture

`User goal → Understand → Discover capabilities → Inspect current state → Reason/plan → Propose actions → Validate → Policy/confirmation → Execute → Run tests/observe → Evaluate → Correct → Report`

The model is never final authority over execution.

## 12. Verification rule

A milestone is not GREEN / VERIFIED / COMPLETE until the user provides the local test receipt.

Remote implementation status and local verification status remain distinct.

No merge is performed unless explicitly requested.

## 13. Current snapshot

**Project:** JARVIS

**Identity:** Third Hand + Second Brain

**Current milestone:** M22.48 Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal → Admission — VERIFIED / COMPLETE.

**Current branch:** `feature/m22.48-adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal-admission`

**Latest verified milestone:** M22.48 — 519/519 (17 focused + 502 core regression).

**Active boundary:** Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal → Admission is complete; next milestone must be derived from the live repository before implementation begins.

**M22.48 source artifact:** `LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission` from `src/tools/learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission.py`.

**M22.48 service:** `LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService`.

**Known namespace rule:** M22.37's `learning_write_adaptation_evaluation_execution_feedback_evaluation.py` remains unchanged. M22.45, M22.46, M22.47, and M22.48 use dedicated result-integrity-feedback evaluation/decision/proposal/admission namespaces to preserve historical import contracts and prevent circular imports.

**Next action:** derive M22.49 from the live repository state and establish its smallest explicit contract before implementation. Do not merge.
