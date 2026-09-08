# Decision 184 — Improvement Decision Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`310e9adb192834e8da390e37ee11cb80b9d5fbb7` — M24.2 Improvement Evaluation Boundary.

## Purpose
M24.3 establishes a bounded decision boundary for exactly one canonical `ImprovementEvaluation`.

The decision records an explicit disposition for the evaluated improvement candidate. It may approve, reject, or defer the candidate for later handling, but it does not itself authorize application, execute the change, mutate policy/model/memory/state, or persist the improvement.

## Contract
- Accepts exactly one canonical `ImprovementEvaluation` artifact.
- Requires the evaluation status to be `EVALUATED`.
- Rechecks evaluation identity and the anchored M24.2 provenance lineage.
- Requires a distinct decision identity.
- Requires explicit decider identity, decision purpose, and decision scope.
- Requires an explicit decision disposition and rationale.
- Preserves evaluation, candidate, and consumed-evidence provenance.
- Recursively freezes decision rationale, factors, and lineage.
- Invalid or lineage-inconsistent evaluations fail closed as `REJECTED`.
- The evaluation artifact is never mutated.

## M24.3 invariant

```text
An improvement evaluation can inform a bounded decision.
A decision cannot authorize, apply, or execute the improvement.
```

## Boundary walls

```text
Improvement Decision ≠ Improvement Application
Improvement Decision ≠ Authorization
Improvement Decision ≠ Execution
Improvement Decision ≠ Policy Mutation
Improvement Decision ≠ Model Mutation
Improvement Decision ≠ Memory Mutation
Improvement Decision ≠ State Mutation
Improvement Decision ≠ Persistence
Improvement Decision ≠ Learning
Improvement Decision ≠ Truth
Improvement Decision ≠ Correctness
Improvement Decision ≠ Certainty
```

An `APPROVED` result means only that the evaluated candidate received an explicit bounded disposition. It does not mean the candidate is authorized, applied, executed, correct, safe, useful, true, certain, or persisted.

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
Improvement Decision                 ← M24.3
  ↓
Improvement Application
  ↓
Verification / Rollback
  ↺ Feedback
```

## Verification
Focused verification covers canonical type enforcement, evaluated-source enforcement, distinct identity, explicit metadata, disposition validation, anchored lineage checks, provenance preservation, immutable evidence, source non-mutation, recursive freezing, rejection behavior, and authority-boundary walls.
