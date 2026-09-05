# JARVIS Master Context

> Canonical cross-chat continuity document for JARVIS. Read this file first at the start of every engineering session, then inspect the current branch/repository state. Repository code/tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's **Third-Hand + Second-Brain**: a personal intelligence and agency system for compounding knowledge, context, experience, projects, and reasoning. It is not defined by one LLM, provider, interface, worker, or plugin.

Core loop:
`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Everything is a capability/plugin. Scraping and automation are backbone capabilities. JARVIS core orchestrates; capabilities implement. Model intelligence is advisory; deterministic boundaries retain execution authority. Safety is structural, not prompt-only. Prefer explicit contracts, composition, small cores, reliable existing mechanisms, and local-first operation.

## 2. Non-negotiable separations

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

## 3. Authority chains

Execution:
`Reasoning → Interpretation → Prioritization → Proposal → Validation → Policy → Confirmation → Confirmation Integrity → Authorization → Authorization Integrity → Sandbox Admission → Execution Preparation/Handoff → Execution Attempt → Outcome`

Current learning/adaptation chain through M22.55:
`Execution Outcome → Execution Feedback → Feedback Evaluation → Learning Candidate → Learning Decision → Learning Write Proposal → Learning Write Admission → Learning Write Execution → Learning Write Outcome → Learning Write Feedback → Learning/Adaptation Evaluation → Adaptation Candidate → Adaptation Decision → Adaptation Proposal → Adaptation Admission → Adaptation Execution → Adaptation Outcome / Result Integrity → Adaptation Feedback → Adaptation Feedback Evaluation → Adaptation Evaluation Decision → Adaptation Evaluation Proposal → Adaptation Evaluation Proposal Admission → Future Adaptation Execution Preparation → Future Adaptation Execution → Future Adaptation Execution Result / Result Integrity → Future Adaptation Execution Feedback → Future Adaptation Execution Feedback Evaluation → Future Adaptation Execution Feedback Decision → Future Adaptation Execution Feedback Proposal → Future Adaptation Execution Feedback Proposal Admission → Future Adaptation Execution Preparation → Future Adaptation Execution → Future Adaptation Execution Result Integrity → Future Adaptation Execution Result Integrity Feedback → Future Adaptation Execution Result Integrity Feedback Evaluation → Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision → Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision Proposal`

A decision is not a proposal; a proposal is not authorization. The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, preparation, execution, result integrity, feedback, and evaluation.

## 4. Cognitive architecture

`Environment/User → Perception/Input → Evidence+Provenance → Memory+Personal Knowledge → World Model/Current Context → Reasoning+Uncertainty → Initiative Candidate → Initiative Evaluation → Proactive Proposal → Value Assessment → Information Gain/Uncertainty Reduction → Bounded Scheduling/Notification Proposal → Proactive Runtime/Feedback → Capability Discovery/Selection → Prioritization → Validation/Policy → Confirmation → Authorization → Execution/Capabilities → Outcome/Feedback → Learning`

## 5. Repository

GitHub: `https://github.com/MrVastoLorde123/JARV1S.git`

Local project directory:
`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion is resolved. Do not reintroduce that workflow.

No merge is performed unless explicitly requested.

## 6. Verified milestone ledger

- M19 — VERIFIED / COMPLETE
- M20 — VERIFIED / COMPLETE
- M21.1–M21.6 — VERIFIED / COMPLETE
- M22.1–M22.51 — VERIFIED / COMPLETE
- M22.52 — VERIFIED / COMPLETE: 15/15 focused + 502/502 core = **517/517**
- M22.53 — VERIFIED / COMPLETE: 13/13 focused + 502/502 core = **515/515**
- M22.54 — VERIFIED / COMPLETE: 15/15 focused + 502/502 core = **517/517**

Selected recent receipts:
- M22.51: **520/520**
- M22.50: **518/518**
- M22.49: **518/518**
- M22.48: **519/519**
- M22.47: **518/518**
- M22.46: **517/517**
- M22.45: **515/515**

## 7. Current verified boundaries

### M22.51 — Execution → Result Integrity
Consumes exactly one M22.50 execution result plus the exact execution request and produces immutable result-integrity evidence. COMPLETED normalizes to SUCCEEDED with deterministic SHA-256 over the logical observed result; FAILED normalizes to FAILED with a non-empty reason and no fingerprint. No authority, retry, revocation, memory mutation, or adaptation truth.

### M22.52 — Result Integrity → Feedback
Consumes exactly one M22.51 result-integrity artifact and produces immutable feedback. Preserves complete known lineage, including `source_proposal_id`, M22.51 `integrity_id`, evaluation lineage, and historical source feedback identity. INTEGRITY_SUCCESS becomes INTEGRITY_SUCCESS feedback; INTEGRITY_FAILURE becomes INTEGRITY_FAILURE feedback. Observational only.

### M22.53 — Feedback → Evaluation
Consumes exactly one M22.52 feedback artifact and produces immutable evaluation evidence. INTEGRITY_SUCCESS becomes `INTEGRITY_SUCCESS_SIGNAL`; INTEGRITY_FAILURE becomes `INTEGRITY_FAILURE_SIGNAL`. Confidence is bounded to [0,1] with deterministic baseline 0.5. Full known lineage is preserved. Evaluation does not establish adaptation truth or authority.

### M22.54 — Evaluation → Decision
Consumes exactly one dedicated M22.53 evaluation artifact and produces one immutable advisory decision. Deterministic baseline:
- failure signal → DEFER
- confidence < 0.5 → DEFER
- otherwise → ACCEPT

Decision identity is deterministic and distinct from upstream identities. Lineage includes `source_proposal_id`. Provider is replaceable. Decision cannot authorize execution, request execution, retry, revoke, mutate memory, grant authority, or establish adaptation truth.

## 8. M22.55 — Decision → Proposal

**Status: IMPLEMENTED / NOT YET LOCALLY VERIFIED.**

Branch:
`feature/m22.55-adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal`

Contract:
`M22.54 Decision → M22.55 Proposal`

M22.55 consumes exactly one M22.54 decision. ACCEPT produces one immutable advisory proposal; DEFER and REJECT produce no proposal. The proposal preserves complete known lineage, adds a deterministic proposal identity, and separates the new proposal identity (`proposal_id`) from upstream decision identity and the inherited `source_proposal_id`.

Proposal payload/evidence/provenance/metadata are recursively immutable. Confidence remains bounded to [0,1]. The proposal is provider-neutral through the upstream decision boundary and is not authorization or execution.

Authority wall:
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Proposal ≠ Retry
- Proposal ≠ Revocation
- Proposal ≠ Memory Mutation
- Proposal ≠ Authority
- Proposal ≠ Adaptation Truth

Dedicated M22.55 namespace:
`src/tools/learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision_proposal.py`

Historical M22.47 proposal namespace remains untouched.

## 9. Namespace rules

M22.45+ uses dedicated namespaces for the future adaptation/result-integrity feedback chain. Historical boundaries remain import-compatible and untouched. Do not collapse new milestones into older modules merely because the class names are similar.

Canonical lineage naming for the current chain uses `source_proposal_id` for inherited proposal lineage where M22.52+ defines it. Do not introduce compatibility aliases unless the contract explicitly requires them.

## 10. Memory and capability architecture

Memory separates decision from mutation: `MemoryDecisionProvider` is provider-neutral/non-mutating; `MemoryDecisionService` selects and validates; `MemoryDecisionExecutor` is the mutation boundary for CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE. Adaptation must not bypass this architecture.

Capability ecosystem: contract/registry, trust/provenance, lifecycle/versioning, permission/policy binding, sandbox, discovery/selection, proposal/invocation, authorization/integrity, preparation, execution attempt, outcome, feedback, learning, and adaptation are explicit boundaries.

Workspace capabilities are `read_file`, `list_directory`, `search_files`, and `write_file`; `write_file` is confirmation-gated.

## 11. Self-work target architecture

`User goal → Understand → Discover capabilities → Inspect current state → Reason/plan → Propose actions → Validate → Policy/confirmation → Execute → Run tests/observe → Evaluate → Correct → Report`

The model is never final authority over execution.

## 12. Verification rule

A milestone is not GREEN / VERIFIED / COMPLETE until the user provides the local test receipt.

Remote implementation status and local verification status remain distinct.

No merge is performed unless explicitly requested.

## 13. Current snapshot

**Latest verified milestone:** M22.54 — 15/15 focused + 502/502 core = **517/517**.

**Active milestone:** M22.55 Decision → Proposal.

**M22.55 status:** implementation exists on its dedicated branch; local verification is pending.

**Next local action:** pull the M22.55 branch and run its focused proposal suite, then the 502-test core regression. Do not mark M22.55 verified until those receipts are supplied.
