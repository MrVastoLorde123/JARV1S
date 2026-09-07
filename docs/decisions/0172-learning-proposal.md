# Decision 172 — Learning Proposal

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`4aeda377d58e89712bc7b028cce52c4b1babf8c3` — M23.159 Learning Eligibility (sealed VERIFIED LOCALLY).

## Purpose
M23.160 establishes a bounded proposal boundary from one learning-eligible artifact.

The mechanism constructs candidate learning changes for a later decision boundary. Proposal formation does not decide, authorize, apply, execute, or persist learning.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningEligibility` artifact.
- Requires eligibility status `ELIGIBLE`; rejected eligibility produces `REJECTED` proposal evidence.
- Requires a distinct proposal identity, proposer identity, proposal purpose, and non-null proposed change.
- Preserves immediate eligibility identity separately from inherited integrity provenance.
- Preserves the complete upstream signal and provenance evidence carried by M23.159.
- Recursively freezes proposed change, rationale, and lineage.
- Produces immutable `PROPOSED` or `REJECTED` evidence.
- `PROPOSED` means only that a candidate learning change was constructed; it is not a learning decision, learning authorization, execution authority, truth, correctness, certainty, or usefulness claim.
- Performs no learner invocation, model update, adaptation, execution, retry authorization, scheduling, persistence, memory mutation, or policy mutation.

## Authority Walls
`Learning Eligibility ≠ Learning Proposal`
`Proposal ≠ Learning Decision`
`Proposal ≠ Learning Authorization`
`Proposal ≠ Execution Authorization`
`PROPOSED ≠ Learned`
`PROPOSED ≠ Authorized`
`PROPOSED ≠ Executed`
`Proposal ≠ Truth`
`Proposal ≠ Correctness`
`Proposal ≠ Certainty`
`Proposal ≠ Usefulness`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity`

## Verification
Local focused verification results:
- Focused M23.160 learning-proposal suite: **11/11 PASS**
- Command: `python -m unittest src.core.tests.test_learning_state_execution_learning_proposal -v`
- Result: `Ran 11 tests in 0.004s` — `OK`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.159.
