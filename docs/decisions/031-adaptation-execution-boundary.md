# Decision 031 — Adaptation Execution Boundary

## Context

M22.25 establishes a non-mutating admission boundary for adaptation proposals. JARVIS now needs a controlled execution seam for an admitted adaptation without collapsing admission into application, authorization, retry, revocation, or memory mutation.

## Decision

Introduce `LearningWriteAdaptationExecutionService`, `LearningWriteAdaptationExecutionRequest`, `LearningWriteAdaptationExecutionResult`, and the provider-neutral `LearningWriteAdaptationApplier` protocol.

Only an `ADMITTED` `LearningWriteAdaptationAdmission` may execute. The exact proposal/admission/decision/candidate/feedback/source-candidate/domain lineage is preserved in the immutable execution request and result. Applier exceptions become explicit `FAILED` results rather than escaping as authority-bearing control flow.

## Authority walls

- Adaptation Admission ≠ Adaptation Execution
- Adaptation Execution Result ≠ Adaptation Truth
- Adaptation Execution ≠ Authorization
- Adaptation Execution ≠ Retry Authorization
- Adaptation Execution ≠ Revocation
- Adaptation Execution ≠ Learning Write
- Adaptation Execution ≠ Memory Mutation
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## Explicit exclusions

This milestone does not define a concrete adaptation store, authorize ordinary tool execution, bypass sandbox/authorization boundaries, automatically retry failures, revoke prior permissions, or establish that an applied adaptation is correct.
