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
- M23.4 — VERIFIED / COMPLETE: 14/14 focused + 549/549 core = **563/563**
- M23.5 — VERIFIED / COMPLETE: 14/14 focused + 563/563 core = **577/577**

Selected recent receipts:
- M23.5: **577/577**
- M23.4: **563/563**
- M23.3: **548/548**
- M23.2: **530/530**
- M23.1: **526/526**

## 7. Verified recent boundaries

### M23.1 — Boundary Composition Contract
**Status: VERIFIED / COMPLETE.** Reusable typed composition primitive for existing JARVIS boundaries. Ordered stages have exact input/output type continuity, immutable observations, explicit stage identity, and fail-closed error wrapping. No implicit retry, skip, branching, authorization, execution, revoke, memory mutation, permission inference, or truth establishment.

Receipt: **12/12 focused + 514/514 core = 526/526**.

### M23.2 — Environment State Contract
**Status: VERIFIED / COMPLETE.** Provider-neutral immutable representation of the environment known to JARVIS across hardware, software, network, models, capabilities, permissions, performance, costs, resources, and metadata. Domain mappings are recursively frozen. Environment state is descriptive, not authoritative, and does not hard-code host-specific discovery.

Receipt: **8/8 focused + 522/522 core = 530/530**.

### M23.3 — Environment Observation Adapter Contract
**Status: VERIFIED / COMPLETE.** Provider-neutral replaceable observation layer composed into M23.2. `EnvironmentObservationAdapter` exposes adapter identity, one explicit environment domain, and `observe(environment_id)`. `EnvironmentObservation` is immutable descriptive evidence. `EnvironmentObservationService` validates adapter/domain/environment continuity and exact observation type; rejects duplicates; wraps failures without retry; composes through M23.2; keeps missing domains empty; and records observation-source identities as metadata. Observation remains non-authorizing and non-mutating.

Receipt:
- Focused: `python -m unittest src.core.tests.test_environment_observation -v` → **13/13 OK**
- Regression: `python -m unittest discover -s src\\core -p "test*.py"` → **535/535 OK**
- Combined: **548/548 OK**

### M23.4 — Environment Observation Freshness/Validity Contract
**Status: VERIFIED / COMPLETE.** Deterministic temporal validity assessment for immutable observations. `EnvironmentObservationFreshnessService` evaluates observation time against assessment time and a non-negative maximum age. `EnvironmentObservationValidity` preserves observation identity, environment identity, domain, timestamps, age bound, and derived freshness. `CURRENT`, `STALE`, `FUTURE`, and `INVALID` are explicit classifications; only `CURRENT` is usable as current by this contract. Timezone-aware timestamps are required and normalized to UTC. Batch assessment preserves order and rejects duplicate observation identities. Raw observations remain unchanged.

Receipt:
- Focused: `python -m unittest src.core.tests.test_environment_observation_freshness -v` → **14/14 OK**
- Regression: `python -m unittest discover -s src\\core -p "test*.py"` → **549/549 OK**
- Combined: **563/563 OK**

### M23.5 — Environment Observation Consistency Contract
**Status: VERIFIED / COMPLETE.** Deterministic comparison of independent observations without selecting authoritative truth. `EnvironmentObservationConsistencyService` compares observations from the same environment and domain; canonical payload comparison yields `CONSISTENT` or `CONFLICTING`. Immutable results preserve both observation identities and adapter identities. Batch comparison is deterministic and preserves pair order while skipping unrelated environments/domains. Duplicate observation identities and invalid input types are rejected. Raw observations are not merged, discarded, mutated, or selected as truth.

M23.3 direct snapshot composition still rejects duplicate domains. M23.5 is the explicit conflict/consistency seam required before a later aggregation contract can combine multiple observers without silently collapsing conflicts.

Files:
- `src/core/environment_observation_consistency.py`
- `src/core/tests/test_environment_observation_consistency.py`
- `docs/decisions/050-environment-observation-consistency-contract.md`

Receipt:
- Focused: `python -m unittest src.core.tests.test_environment_observation_consistency -v` → **14/14 OK**
- Regression: `python -m unittest discover -s src\\core -p "test*.py"` → **563/563 OK**
- Combined: **577/577 OK**

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

Remote implementation and local verification remain distinct.

No merge is performed unless explicitly requested.

## 12. Current snapshot

**Latest verified milestone:** M23.5 — 14/14 focused + 563/563 core = **577/577**.

**Active milestone:** M23.6 — Environment Observation Aggregation Contract.

**M23.6 status:** NOT YET IMPLEMENTED.

**Next engineering action:** define a deterministic aggregation boundary that can combine multiple observations for one environment/domain only after consistency/freshness evidence is available, while preserving source lineage and never silently selecting conflicting evidence as truth. No merge performed.
