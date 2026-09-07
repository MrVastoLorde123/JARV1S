# Decision 150 — Learning-State Consumption Read Validation Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`35a91afdd3f92291e9dc6024722c9caef67a952e` — M23.137 Learning-State Durable Read Consumption (sealed VERIFIED LOCALLY).

## Purpose
M23.138 establishes the validation boundary after a durable-state read has been explicitly performed.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningStateDurableReadConsumption` artifact and evaluates whether the recorded read evidence is internally consistent enough for a later consumer. Validation checks the read status, identity, lineage, bounded-read scope, payload/fingerprint consistency, and immutable evidence invariants. It does not reread durable state, repair the source artifact, reinterpret its payload, establish truth, or authorize downstream action.

## Contract
- Accepts exactly one canonical M23.137 durable-read consumption artifact.
- Requires the source read status to be `READ`; rejected reads fail closed without becoming validated.
- Requires an explicit validation identity, validator identity, validation purpose, and rationale.
- Requires validation identity to be distinct from the source read identity.
- Requires source lineage to preserve the read and upstream consumption-request and source-validation identities.
- Requires the recorded read fingerprint to equal a fresh SHA-256 recomputation of the recorded read payload.
- Requires both recorded and computed fingerprints to be exactly 64 lowercase hexadecimal SHA-256 characters.
- Requires a successful read to contain non-`None` payload evidence.
- Requires the requested scope to be a mapping whose `state_key` agrees with the recorded state key.
- When `fields` are present, requires a non-empty distinct sequence of field names and a payload mapping whose keys match the requested field set exactly.
- Preserves read, consumption-request, source-validation, integrity, transition, evidence, state-key, scope, reader, purpose, and confidence provenance.
- Emits recursively immutable validation evidence.
- Does not reread durable state, mutate the source read, repair fingerprints or payloads, interpret payload meaning, learn, execute, authorize, schedule, plan, or persist anything.

## Authority Walls
`Consumption Read Validation ≠ Durable-State Read`
`Consumption Read Validation ≠ Durable-State Mutation`
`Consumption Read Validation ≠ Persistence`
`Consumption Read Validation ≠ Interpretation`
`Consumption Read Validation ≠ Learning`
`Consumption Read Validation ≠ Truth`
`Consumption Read Validation ≠ Correctness`
`Consumption Read Validation ≠ Certainty`
`Consumption Read Validation ≠ Usefulness`
`Consumption Read Validation ≠ Authorization`
`VALIDATED ≠ Consumed`
`VALIDATED ≠ Applied`
`VALIDATED ≠ Persisted`
`VALIDATED ≠ Executed`

M23.138 therefore validates the evidence of a read without granting authority to act on what was read.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
Focused verification: **21/21 M23.138 tests passed**.

Regression exercised in the same focused invocation: **20/20 M23.137 tests passed**.

Combined result: **41/41 tests passed, 0 failures, 0 errors**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.137.
