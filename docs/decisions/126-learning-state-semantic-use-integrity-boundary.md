# Decision 126 — Learning-State Semantic Use Integrity Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`18c3342ab442e2dd7a89aadbc8bc670b4dab2a5b` — M23.113 Learning-State Semantic Use Validation Boundary.

## Purpose
M23.114 establishes the bounded integrity boundary immediately after semantic-use validation. It verifies that one M23.113 validation artifact is internally consistent and emits immutable integrity evidence for downstream handling.

Integrity here is structural evidence about the representation presented to the boundary. It does not decide whether the semantic result is true, correct, certain, useful, learnable, authoritative, permissible, or executable.

## Contract
- Consumes exactly one canonical `LearningStateSemanticUseValidation` artifact.
- Requires validation status `ACCEPTED` and a mapping semantic-use result.
- Requires a non-empty integrity identity.
- Preserves validation, use, request, interpretation, source, transition, evidence, application, state-key, confidence, consumer, purpose, provenance, and fingerprint identities.
- Preserves the returned semantic-use result as recursively frozen integrity evidence.
- Emits immutable reasons and lineage.
- Fails closed on wrong source type, blank integrity identity, inconsistent validation/integrity status, or invalid required fields.
- Does not inspect semantic values or infer meaning from them.
- Does not establish truth, correctness, certainty, usefulness, learning, model update, memory mutation, policy mutation, authorization, permission, planning, scheduling, or execution.

## Authority Walls
`Semantic Use Integrity ≠ Semantic Truth`
`Integrity ≠ Correctness`
`Integrity ≠ Certainty`
`Integrity ≠ Learning`
`Integrity ≠ Model Update`
`Integrity ≠ Memory Mutation`
`Integrity ≠ Authorization`
`Integrity ≠ Permission`
`Integrity ≠ Planning`
`Integrity ≠ Execution`

M23.114 only establishes that an accepted semantic-use validation artifact is internally consistent with this integrity contract.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → (future downstream handling)`

## Verification Plan
Focused tests cover exact input-type gating, accepted/rejected validation gating, integrity identity requirements, provenance/fingerprint preservation, recursive result immutability, source non-mutation, deterministic formation, semantic non-judgment, required-status validation, and absence of learning/authority/execution powers.

Local verification will be recorded here after the focused and core regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.113.