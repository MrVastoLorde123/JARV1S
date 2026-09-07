# Decision 129 — Learning-State Semantic Use Consumption Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`fa9ef4b163ba78aa1cf12eb69ac0698046e1ef8e` — M23.116 Learning-State Semantic Use Receipt Boundary.

## Purpose
M23.117 establishes the smallest bounded mechanism that actually consumes a received semantic-use artifact. It joins the original sealed handoff with its matching receipt, reads the semantic result, and emits immutable consumption evidence.

Consumption here means bounded reading/use of an already-received semantic artifact. It does not make a semantic judgment, establish truth or correctness, learn from the result, mutate memory or policy, grant authority, plan work, schedule work, or execute an action.

## Contract
- Consumes exactly one canonical `LearningStateSemanticUseHandoff` and its matching `LearningStateSemanticUseReceipt`.
- Requires handoff status `READY` and receipt status `RECEIVED`.
- Requires exact handoff/receipt identity agreement and matching recipient identity.
- Reads the handoff semantic result and preserves it as recursively frozen consumption evidence.
- Preserves handoff, receipt, integrity, validation, use, request, interpretation, source, transition, evidence, application, state-key, confidence, consumer, purpose, provenance, and fingerprint identities.
- Emits immutable consumption reasons and lineage.
- Fails closed on wrong source types, invalid statuses, identity mismatch, recipient mismatch, or invalid required fields.
- Does not transform or interpret the semantic result.

## Authority Walls
`Semantic Use Consumption ≠ Semantic Truth`
`Consumption ≠ Correctness`
`Consumption ≠ Certainty`
`Consumption ≠ Usefulness`
`Consumption ≠ Learning`
`Consumption ≠ Model Update`
`Consumption ≠ Memory Mutation`
`Consumption ≠ Policy Mutation`
`Consumption ≠ Authorization`
`Consumption ≠ Permission`
`Consumption ≠ Planning`
`Consumption ≠ Scheduling`
`Consumption ≠ Execution`

M23.117 only records bounded consumption of a received semantic-use artifact.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → (future downstream semantic handling)`

## Verification Plan
Focused tests cover exact input-type gating, READY/RECEIVED status gating, handoff/receipt identity agreement, recipient matching, semantic-result reading, recursive immutability, provenance/fingerprint preservation, source non-mutation, deterministic formation, non-transformation/non-interpretation, and absence of learning/authority/execution powers.

Local verification results:
- Focused M23.117 suite: **18/18 PASS**
- Full `src/core/tests` regression suite: **1783/1783 PASS**

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.116.
