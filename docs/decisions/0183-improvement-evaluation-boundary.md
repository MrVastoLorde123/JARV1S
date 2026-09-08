# Decision 183 — Improvement Evaluation Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`d3e284fc0a06322c5de5cb57b3ec9b7984088e93` — M24.1 Continuous Self-Improvement Candidate Boundary.

## Purpose
M24.2 establishes a bounded evaluation boundary for exactly one canonical `ContinuousSelfImprovementCandidate`.

The evaluation records structured observations about the candidate against explicitly supplied evaluation criteria. It does not authorize, decide, apply, execute, persist, or otherwise activate the proposed improvement.

## Contract
- Accepts exactly one canonical `ContinuousSelfImprovementCandidate` artifact.
- Requires the candidate status to be `PROPOSED`.
- Rechecks candidate identity and the anchored M24.1 provenance lineage.
- Requires a distinct evaluation identity.
- Requires explicit evaluator identity, evaluation purpose, and evaluation scope.
- Requires explicit non-empty evaluation criteria and observations.
- Requires a bounded assessment classification without converting evaluation into an application decision.
- Preserves candidate provenance needed to trace the evaluation back to consumed learning-state evidence.
- Recursively freezes criteria, observations, and lineage.
- Invalid or lineage-inconsistent candidates fail closed as `REJECTED`.
- The candidate is never mutated.

## M24.2 invariant

```text
A self-improvement candidate can be evaluated.
An evaluation cannot authorize, decide, or apply the candidate.
```

## Boundary walls

```text
Improvement Evaluation ≠ Improvement Decision
Improvement Evaluation ≠ Authorization
Improvement Evaluation ≠ Execution
Improvement Evaluation ≠ Application
Improvement Evaluation ≠ Policy Mutation
Improvement Evaluation ≠ Model Mutation
Improvement Evaluation ≠ Memory Mutation
Improvement Evaluation ≠ Persistence
Improvement Evaluation ≠ Learning
Improvement Evaluation ≠ Truth
Improvement Evaluation ≠ Correctness
Improvement Evaluation ≠ Certainty
```

An `EVALUATED` result means only that bounded evaluation evidence was formed for the proposed candidate. Its assessment does not mean the candidate is approved, safe, correct, useful, authorized, or applied.

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
Improvement Evaluation              ← M24.2
  ↓
Improvement Decision
  ↓
Improvement Application
  ↓
Verification / Rollback
  ↺ Feedback
```

## Verification
Focused verification covers canonical type enforcement, proposed-source enforcement, distinct identity, explicit metadata, criteria validation, anchored lineage checks, bounded assessment classification, immutable evidence, source non-mutation, recursive freezing, rejection behavior, provenance preservation, and authority-boundary walls.

Local verification completed:

```text
33 focused tests: PASS
90 focused + regression tests: PASS
2741 core tests: PASS
```