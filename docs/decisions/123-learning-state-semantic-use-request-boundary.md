# Decision 123 — Learning-State Semantic Use Request Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`60a3f8e633fcec5ec7e68bb389bd73c707d7b4be` — M23.110 Learning-State Interpretation Validation Integrity Boundary.

## Purpose
M23.111 creates the next bounded handoff after interpretation-validation integrity. A valid M23.110 integrity artifact may be converted into an immutable request for a downstream semantic consumer. The request identifies what evidence may be supplied for semantic use without performing semantic use itself.

## Contract
- Consumes exactly one canonical `LearningStateInterpretationValidationIntegrity` artifact.
- Requires integrity status `VALID` and validation status `ACCEPTED`.
- Requires a non-empty request identity, consumer identity, and use purpose.
- Preserves all learning-state provenance, lineage, state-key, fingerprint, confidence, and interpretation identities.
- Carries the recursively frozen interpretation evidence without inspecting or changing its semantic values.
- Emits immutable request metadata, reasons, and lineage.
- Does not interpret, summarize, classify, rank, infer, judge truth/correctness/certainty/usefulness, learn, update models, mutate memory or policy, authorize, grant permission, schedule, plan, or execute.
- Repeated construction from equivalent integrity evidence and equivalent request metadata is deterministic except for the caller-supplied request identity.

## Authority Walls
`Semantic Use Request ≠ Semantic Interpretation`
`Request ≠ Truth`
`Request ≠ Correctness`
`Request ≠ Certainty`
`Request ≠ Learning`
`Request ≠ Model Update`
`Request ≠ Memory Mutation`
`Request ≠ Authorization`
`Request ≠ Permission`
`Request ≠ Planning`
`Request ≠ Execution`

M23.111 only establishes a bounded, immutable request for downstream semantic use of already-integrity-validated evidence.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → (future semantic use)`

## Verification Plan
Focused tests cover valid-integrity gating, rejected/invalid gating, exact input-type gating, request metadata validation, provenance/fingerprint preservation, interpretation preservation and recursive immutability, deterministic request formation, semantic non-judgment, and absence of learning/authority/execution powers.

Verified locally:
- Focused verification: **15/15**.
- Core regression: **1687/1687**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.110.
