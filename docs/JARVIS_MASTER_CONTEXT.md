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

Current learning/adaptation chain through M22.56 remains unchanged.

A decision is not a proposal; a proposal is not authorization; admission is not authorization. The final mutation boundary remains downstream from evidence, reasoning, decisions, proposals, policy, admission, preparation, execution, result integrity, feedback, and evaluation.

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
- M22.55 — VERIFIED / COMPLETE: 15/15 focused + 502/502 core = **517/517**
- M22.56 — VERIFIED / COMPLETE: 16/16 focused + 502/502 core = **518/518**
- M23.1 — VERIFIED / COMPLETE: 12/12 focused + 514/514 core = **526/526**
- M23.2 — VERIFIED / COMPLETE: 8/8 focused + 522/522 core = **530/530**
- M23.3 — VERIFIED / COMPLETE: 13/13 focused + 535/535 core = **548/548**

Selected recent receipts:
- M23.3: **548/548**
- M23.2: **530/530**
- M23.1: **526/526**
- M22.56: **518/518**
- M22.55: **517/517**
- M22.54: **517/517**

## 7. Verified recent boundaries

### M23.1 — Boundary Composition Contract
**Status: VERIFIED / COMPLETE.** Reusable typed composition primitive for existing JARVIS boundaries. Ordered stages have exact input/output type continuity, immutable observations, explicit stage identity, and fail-closed error wrapping. No implicit retry, skip, branching, authorization, execution, revoke, memory mutation, permission inference, or truth establishment.

Receipt: **12/12 focused + 514/514 core = 526/526**.

### M23.2 — Environment State Contract
**Status: VERIFIED / COMPLETE.** Provider-neutral immutable representation of the environment known to JARVIS across hardware, software, network, models, capabilities, permissions, performance, costs, resources, and metadata. Domain mappings are recursively frozen. Environment state is descriptive, not authoritative, and does not hard-code host-specific discovery.

Receipt: **8/8 focused + 522/522 core = 530/530**.

### M23.3 — Environment Observation Adapter Contract
**Status: VERIFIED / COMPLETE.** Provider-neutral replaceable observation layer composed into M23.2.

`EnvironmentObservationAdapter` exposes an adapter identity, one explicit environment domain, and `observe(environment_id)`. `EnvironmentObservation` is immutable descriptive evidence tied to one adapter, environment, and domain. `EnvironmentObservationService` validates adapter identity, domain identity, environment identity, and exact observation type; rejects duplicate adapter IDs/domains; wraps adapter failures without retry; composes accepted observations through `EnvironmentSnapshotService`; keeps missing domains empty; and retains observation source identities as descriptive metadata.

Authority boundary: observation does not authorize execution, elevate permissions, imply capability executability, retry, revoke, mutate memory, or establish adaptation truth.

Receipt:
- Focused: `python -m unittest src.core.tests.test_environment_observation -v` → **13/13 OK**
- Regression: `python -m unittest discover -s src\\core -p "test*.py"` → **535/535 OK**
- Combined: **548/548 OK**

## 8. Namespace and lineage rules

M22.45+ uses dedicated namespaces for the future adaptation/result-integrity feedback chain. Historical boundaries remain import-compatible and untouched. Do not collapse new milestones into older modules merely because class names are similar.

Canonical lineage naming uses `source_proposal_id` for inherited proposal lineage where defined. When a boundary introduces an immediate upstream identity with the same conceptual domain, preserve distinct roles explicitly rather than aliasing them.

Do not introduce compatibility aliases unless the contract explicitly requires them.

## 9. Memory and capability architecture

Memory separates decision from mutation: `MemoryDecisionProvider` is provider-neutral/non-mutating; `MemoryDecisionService` selects and validates; `MemoryDecisionExecutor` is the mutation boundary for CREATE, CONFIRM, UPDATE, CONTRADICT, or IGNORE. Adaptation must not bypass this architecture.

Capability ecosystem: contract/registry, trust/provenance, lifecycle/versioning, permission/policy binding, sandbox, discovery/selection, proposal/invocation, authorization/integrity, preparation, execution attempt, outcome, feedback, learning, and adaptation are explicit boundaries.

Workspace capabilities are `read_file`, `list_directory`, `search_files`, and `write_file`; `write_file` is confirmation-gated.

## 10. Self-work target architecture

`User goal → Understand → Discover capabilities → Inspect current state → Reason/plan → Propose actions → Validate → Policy/confirmation → Execute → Run tests/observe → Evaluate → Correct → Report`

The model is never final authority over execution.

## 11. Verification rule

A milestone is not GREEN / VERIFIED / COMPLETE until the user provides the local test receipt.

Remote implementation status and local verification status remain distinct.

No merge is performed unless explicitly requested.

## 12. Current snapshot

**Latest verified milestone:** M23.3 — 13/13 focused + 535/535 core = **548/548**.

**Active milestone:** M23.4 — Environment Observation Freshness/Validity Contract.

**M23.4 status:** NOT YET IMPLEMENTED.

**Next engineering action:** establish deterministic freshness/validity semantics for environment observations, preserving raw observation evidence while preventing stale state from being treated as current state. The contract should remain provider-neutral, immutable, composable with M23.3/M23.2, and non-authorizing. No merge performed.
