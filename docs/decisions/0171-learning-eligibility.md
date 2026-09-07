# Decision 171 — Learning Eligibility

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`f06c2a4e525837f605f462f87ca259afc4e9b6be` — M23.158 Learning Signal Integrity (sealed VERIFIED LOCALLY).

## Purpose
M23.159 establishes a bounded learning-eligibility gate for one learning-signal integrity artifact.

The boundary determines only whether integrity-validated learning evidence may enter a future learner path. Eligibility does not perform learning, update a model, mutate memory, authorize learning, authorize execution, schedule work, or establish truth, correctness, certainty, or usefulness.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningSignalIntegrity` artifact.
- Requires integrity status `VALID`; invalid integrity evidence fails closed to `REJECTED`.
- Requires a distinct eligibility identity, explicit learner identity, and explicit eligibility purpose.
- Preserves immediate integrity identity separately from inherited upstream integrity provenance.
- Preserves the complete M23.158 signal, evaluation, execution, request, interpretation, receipt, handoff, consumption, and provenance evidence needed by the next learning boundary.
- Produces recursively immutable `ELIGIBLE` or `REJECTED` evidence.
- `ELIGIBLE` means only that the integrity artifact satisfied this learning-entry gate; it is not learning, learning authorization, execution authority, truth, correctness, certainty, or usefulness.
- Performs no learner invocation, model update, adaptation, execution, retry authorization, scheduling, persistence, memory mutation, or policy mutation.

## Authority Walls
`Signal Integrity ≠ Learning Eligibility`
`Eligibility ≠ Learning`
`Eligibility ≠ Learning Authorization`
`Eligibility ≠ Execution Authorization`
`ELIGIBLE ≠ Learned`
`ELIGIBLE ≠ Authorized`
`ELIGIBLE ≠ Executed`
`Eligibility ≠ Truth`
`Eligibility ≠ Correctness`
`Eligibility ≠ Certainty`
`Eligibility ≠ Usefulness`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity`

## Verification
Local focused verification results:
- Focused M23.159 learning-eligibility suite: **12/12 PASS**
- Command: `python -m unittest src.core.tests.test_learning_state_execution_learning_eligibility -v`
- Result: `Ran 12 tests in 0.004s` — `OK`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.158.
