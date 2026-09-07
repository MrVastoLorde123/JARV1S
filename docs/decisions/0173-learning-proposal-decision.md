# Decision 173 — Learning Proposal Decision

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`91806e92da3a5332e77fb56ed5fb4bf32972c7bd` — M23.160 Learning Proposal (sealed VERIFIED LOCALLY).

## Purpose
M23.161 establishes the explicit decision boundary for one learning proposal.

The mechanism records whether a proposed learning change is approved or rejected. Decision evidence does not apply the proposal, authorize execution, mutate durable state, or perform learning.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposal` artifact.
- Requires proposal status `PROPOSED`; rejected proposals fail closed to `REJECTED` decision evidence.
- Requires a distinct decision identity, explicit decision-maker identity, decision purpose, and decision rationale.
- Preserves the immediate proposal identity separately from all inherited upstream provenance.
- Preserves the complete proposal, eligibility, integrity, signal, execution, semantic-use, and provenance evidence needed by the application boundary.
- Recursively freezes proposed change, proposal rationale, decision rationale, and lineage.
- Produces immutable `APPROVED` or `REJECTED` decision evidence.
- `APPROVED` means only that this decision boundary accepted the proposal as a candidate for the next application boundary; it does not apply learning, authorize execution, grant retry authority, mutate state, or establish truth.
- Performs no learner invocation, model update, adaptation, proposal application, execution, retry authorization, scheduling, persistence, memory mutation, or policy mutation.

## Authority Walls
`Learning Proposal ≠ Learning Proposal Decision`
`Decision ≠ Proposal Application`
`Decision ≠ Learning Authorization`
`Decision ≠ Execution Authorization`
`APPROVED ≠ Applied`
`APPROVED ≠ Learned`
`APPROVED ≠ Executed`
`Decision ≠ Truth`
`Decision ≠ Correctness`
`Decision ≠ Certainty`
`Decision ≠ Usefulness`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity`

## Verification
Local focused verification results:
- Focused M23.161 learning-proposal-decision suite: **11/11 PASS**
- Command: `python -m unittest src.core.tests.test_learning_state_execution_learning_proposal_decision -v`
- Result: `Ran 11 tests in 0.004s` — `OK`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.160.