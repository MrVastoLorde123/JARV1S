# Decision 176 — Learning-State Evidence Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`ea3a6a42f82f2c7fa7cac2625233bdc1b24c17d7` — M23.163 Learning Proposal Application Integrity.

## Purpose
M23.164 establishes a bounded evidence-recording boundary after proposal-application integrity verification.

This boundary records structured evidence about a candidate learning-state effect. It does not transition state, mutate durable state, persist state, learn, authorize learning or execution, retry, schedule, or establish truth/correctness/certainty/usefulness.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalApplicationIntegrity` artifact.
- Requires explicit evidence identity, collector, purpose, rationale, and payload.
- Requires the upstream integrity artifact to be `VALID` with an internally consistent anchored integrity/application/source-integrity lineage.
- A `VALID` integrity artifact produces `RECORDED` evidence; invalid or tampered integrity evidence fails closed as `REJECTED`.
- Preserves immediate integrity identity and complete upstream provenance without mutation.
- Preserves caller-supplied evidence lineage rather than rewriting it.
- Recursively freezes evidence payload, rationale, and lineage.
- Produces an immutable evidence artifact.
- `RECORDED` means only that bounded evidence was formed from a valid integrity artifact; it does not mean that learning occurred or that state changed.

## Authority Walls
`Application Integrity ≠ State Evidence`
`Evidence ≠ State Transition`
`Evidence ≠ Persistence`
`Evidence ≠ Learning`
`Evidence ≠ Authorization`
`RECORDED ≠ Applied`
`RECORDED ≠ Learned`
`RECORDED ≠ Executed`
`RECORDED ≠ True`
`RECORDED ≠ Correct`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation`

## Verification
Focused local verification completed:
`python -m unittest src.core.tests.test_learning_state_execution_learning_state_evidence -v`

Result: `Ran 15 tests in 0.006s — OK`

## Atomicity
Exactly **1 commit / 3 intended files** from M23.163. No merge is implied by this decision.
