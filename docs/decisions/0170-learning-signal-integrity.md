# Decision 170 — Learning Signal Integrity

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`c9434aeefefb0b2454d08dddb56b14ae66c090a6` — M23.157 Evaluation → Learning Signal (sealed VERIFIED LOCALLY).

## Purpose
M23.158 establishes the bounded integrity boundary for one recorded learning-signal artifact.

The mechanism verifies canonical learning-signal evidence and emits immutable integrity evidence. Integrity verification does not reinterpret the signal, repair it, authorize learning, establish truth, or grant execution authority.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningSignal` artifact.
- Requires learning-signal status `RECORDED`; rejected signals fail closed.
- Requires a distinct integrity identity and a supplied SHA-256 signal fingerprint.
- Checks the signal's anchored and inherited provenance without rereading or repairing upstream artifacts.
- Recomputes the canonical signal fingerprint and rejects mismatches.
- Preserves explicit signal classification, purpose, context, execution evidence, and inherited provenance.
- Produces recursively immutable `VALID` or `INVALID` integrity evidence with separate integrity identity.
- `VALID` means only that the supplied signal satisfied this integrity boundary; it is not truth, correctness, certainty, usefulness, learning eligibility, authorization, or execution authority.
- Performs no repair, learner invocation, model update, adaptation, execution, retry authorization, scheduling, persistence, memory mutation, policy mutation, or durable-state mutation.

## Authority Walls
`Learning Signal ≠ Signal Integrity`
`Integrity ≠ Truth`
`Integrity ≠ Correctness`
`Integrity ≠ Certainty`
`Integrity ≠ Usefulness`
`Integrity ≠ Learning Eligibility`
`VALID ≠ Learned`
`VALID ≠ Authorized`
`VALID ≠ Executed`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity`

## Verification
Local focused verification results:
- Focused M23.158 learning-signal integrity suite: **22/22 PASS**
- Command: `python -m unittest src.core.tests.test_learning_state_execution_learning_state_execution_learning_signal_integrity -v`
- Result: `Ran 22 tests in 0.017s` — `OK`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.157.
