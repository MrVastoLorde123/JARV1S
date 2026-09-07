# Decision 174 — Learning Proposal Application

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`71e99c1eb181e6ac836b0433921eacc431ae15f3` — M23.161 Learning Proposal Decision (sealed VERIFIED LOCALLY).

## Purpose
M23.162 establishes the explicit application boundary for one learning-proposal decision.

The mechanism records whether an approved proposal decision crossed the application boundary. Application evidence is immutable and bounded; it does not itself grant learning authority, authorize execution, invoke a learner, mutate durable state, or establish truth.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalDecision` artifact.
- Requires a distinct application identity, explicit applier identity, application purpose, and application rationale.
- `APPROVED` decisions produce `APPLIED` application evidence; non-approved decisions fail closed to `REJECTED` application evidence.
- Preserves the immediate decision identity separately from the proposal, eligibility, integrity, signal, evaluation, feedback, execution, semantic-use, and provenance evidence inherited from upstream boundaries.
- Preserves the proposed change and decision rationale without mutating the source decision.
- Recursively freezes application rationale, application evidence, inherited proposed-change evidence, and lineage.
- Produces immutable `APPLIED` or `REJECTED` application evidence.
- `APPLIED` means only that the proposal crossed this application boundary; it does not mean the system has learned, authorized execution, scheduled work, invoked a learner, mutated memory or policy, or established truth/correctness/certainty/usefulness.
- Performs no learner invocation, model update, adaptation authorization, execution authorization, retry authorization, scheduling, persistence, memory mutation, or policy mutation.

## Authority Walls
`Learning Proposal Decision ≠ Proposal Application`
`Application ≠ Learning`
`Application ≠ Learning Authorization`
`Application ≠ Execution Authorization`
`APPLIED ≠ Learned`
`APPLIED ≠ Authorized`
`APPLIED ≠ Executed`
`Application ≠ Truth`
`Application ≠ Correctness`
`Application ≠ Certainty`
`Application ≠ Usefulness`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation`

## Verification
Local focused verification:
- M23.162 learning-proposal-application suite: **10/10 PASS**
- Command: `python -m unittest src.core.tests.test_learning_state_execution_learning_proposal_application -v`
- Result: `Ran 10 tests in 0.003s` — `OK`

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.161.
