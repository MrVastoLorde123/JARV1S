# Decision 175 — Learning Proposal Application Integrity

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`7ff5f67dde659c449b9dacdb357a65a3bb023472` — M23.162 Learning Proposal Application.

## Purpose
M23.163 establishes the integrity boundary for one learning-proposal application artifact.

The mechanism verifies structural identity, anchored lineage, and a deterministic SHA-256 fingerprint of the application evidence. Integrity evidence observes the application; it does not repair, reapply, learn, authorize execution, or establish correctness.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningProposalApplication` artifact.
- Requires a distinct integrity identity.
- Preserves application identity and complete upstream provenance.
- Computes a deterministic SHA-256 fingerprint over the application evidence.
- Detects mismatched application fingerprints and anchored application/decision lineage.
- Preserves supplied invalid evidence rather than silently repairing it.
- Produces immutable `VALID` or `INVALID` integrity evidence.
- Recursively freezes copied evidence and lineage.
- `VALID` means only that this integrity boundary's structural and fingerprint checks passed; it does not establish truth, correctness, certainty, usefulness, learning, authorization, or execution safety.
- Performs no repair, learner invocation, model update, execution, retry authorization, scheduling, persistence, memory mutation, or policy mutation.

## Authority Walls
`Proposal Application ≠ Application Integrity`
`Integrity ≠ Repair`
`Integrity ≠ Learning`
`Integrity ≠ Learning Authorization`
`Integrity ≠ Execution Authorization`
`VALID ≠ Correct`
`VALID ≠ True`
`VALID ≠ Certain`
`VALID ≠ Useful`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation`

## Verification
Local focused verification completed successfully:
```text
Ran 15 tests in 0.007s
OK
```

Command:
`python -m unittest src.core.tests.test_learning_state_execution_learning_proposal_application_integrity -v`

## Atomicity
Exactly **1 commit / 3 intended files** from M23.162. No merge is implied by this decision.
