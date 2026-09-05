# Decision 032 — Adaptation Execution Outcome / Result Integrity Boundary

## Context

M22.26 executes an admitted adaptation proposal through a replaceable applier and returns an immutable execution result. That result is an observation of what the applier reported, not proof that the adaptation was correct or desirable.

## Decision

Introduce `LearningWriteAdaptationOutcomeService` and `LearningWriteAdaptationOutcome` as the integrity/normalization boundary after adaptation execution.

The boundary:

- consumes the exact `LearningWriteAdaptationExecutionResult` and `LearningWriteAdaptationExecutionRequest` pair;
- verifies execution, admission, proposal, decision, candidate, feedback, source-candidate, and domain identity;
- normalizes completed execution to `SUCCEEDED` and failed execution to `FAILED`;
- deterministically fingerprints successful adaptation results;
- preserves immutable outcome lineage;
- remains non-authorizing and non-mutating.

## Authority walls

- Adaptation Execution Result ≠ Adaptation Outcome
- Adaptation Outcome ≠ Adaptation Truth
- Result Fingerprint ≠ Truth
- Outcome ≠ Authorization
- Outcome ≠ Retry Authorization
- Outcome ≠ Revocation
- Outcome ≠ Memory Mutation
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## Explicit exclusions

This milestone does not evaluate whether an adaptation is correct, approve future retries, authorize capabilities, revoke permissions, mutate learning or memory, or define adaptation feedback persistence.
