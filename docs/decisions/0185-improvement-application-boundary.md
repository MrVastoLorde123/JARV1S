# Decision 185 — Improvement Application Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`f6974b949aa966c0d1f000f3dab8e63db839000a` — M24.3 Improvement Decision Boundary.

## Purpose
M24.4 establishes a bounded application boundary for exactly one approved `ImprovementDecision`.

The application artifact records the outcome of an externally performed improvement application. The core service does not invoke an executor, mutate model/memory/policy/state, persist state, or establish truth/correctness/certainty.

## Contract
- Accepts exactly one canonical `ImprovementDecision` artifact.
- Requires the decision status to be `APPROVED`.
- Rechecks decision identity and the anchored M24.3 provenance lineage.
- Reuses the application identity already threaded through the upstream provenance chain.
- Requires explicit applicator identity, application purpose, and application scope.
- Requires explicit application result evidence and typed application status.
- Preserves decision, evaluation, candidate, and consumed-evidence provenance.
- Recursively freezes application result evidence and lineage.
- Invalid or lineage-inconsistent decisions fail closed as `INVALID`.
- The decision artifact is never mutated.

## M24.4 invariant

```text
An approved improvement decision can produce an immutable application record.
The application record cannot itself execute or authorize execution.
```

## Boundary walls

```text
Improvement Application ≠ Execution
Improvement Application ≠ Executor Invocation
Improvement Application ≠ Model Mutation
Improvement Application ≠ Memory Mutation
Improvement Application ≠ Policy Mutation
Improvement Application ≠ State Mutation
Improvement Application ≠ Persistence
Improvement Application ≠ Learning
Improvement Application ≠ Truth
Improvement Application ≠ Correctness
Improvement Application ≠ Certainty
Improvement Application ≠ Usefulness
```

An `APPLIED` result means only that an external application step reported an applied outcome and that this report passed the bounded lineage checks. It does not grant the artifact execution authority or prove correctness of the resulting system state.

## Architecture

```text
Execution Outcome
  ↓
Feedback
  ↓
Evaluation
  ↓
Learning Signal
  ↓
Learning Eligibility / Proposal
  ↓
Learning-State Validation
  ↓
Validation Integrity
  ↓
Validation-Integrity Consumption
  ↓
Continuous Self-Improvement Candidate
  ↓
Improvement Evaluation
  ↓
Improvement Decision
  ↓
Improvement Application          ← M24.4
  ↓
Verification / Rollback
  ↺ Feedback
```

## Verification
Focused verification covers exact decision type enforcement, approved-source enforcement, anchored lineage checks, application identity preservation, required metadata, typed status/result evidence, provenance preservation, recursive immutability, source non-mutation, fail-closed invalidation, and execution/authority boundary walls.
