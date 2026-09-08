# Decision 182 — Continuous Self-Improvement Candidate Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`e733e16ed73507793f7ea6c5332985a14b46f634` — M23.169 Learning-State Validation-Integrity Consumption Boundary.

## Purpose
M24.1 establishes the first active continuous-self-improvement boundary. It converts exactly one consumed, validated learning-state integrity artifact into one immutable improvement candidate.

The candidate records a proposed change to JARVIS behavior or configuration for later evaluation. It is not itself learning, authorization, execution, policy mutation, model mutation, memory mutation, or persistence.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateValidationIntegrityConsumption` artifact.
- Requires the source consumption status to be `CONSUMED`.
- Rechecks source consumption identity, integrity identity, validation identity, transition identity, evidence identity, application identity, source integrity identity, and source validation identity.
- Requires a distinct candidate identity.
- Requires explicit proposer identity and candidate purpose.
- Requires a non-null proposed improvement and rationale.
- Preserves the consumed source provenance and a deterministic improvement scope.
- Recursively freezes proposed improvement, rationale, scope, and lineage.
- Invalid or lineage-inconsistent consumed evidence fails closed as `REJECTED`.
- The source consumption artifact is never mutated.

## M24 invariant

```text
Learning evidence can produce an improvement candidate.
An improvement candidate cannot grant itself authority.
```

## Boundary walls

```text
Improvement Candidate ≠ Learning
Improvement Candidate ≠ Authorization
Improvement Candidate ≠ Execution
Improvement Candidate ≠ Policy Mutation
Improvement Candidate ≠ Model Mutation
Improvement Candidate ≠ Memory Mutation
Improvement Candidate ≠ Persistence
Improvement Candidate ≠ Truth
Improvement Candidate ≠ Correctness
Improvement Candidate ≠ Certainty
```

A `PROPOSED` result means only that a bounded improvement candidate was formed from valid consumed learning-state evidence. It does not mean the proposed change is correct, safe, useful, authorized, or applied.

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
Continuous Self-Improvement Candidate   ← M24.1
  ↓
Improvement Evaluation
  ↓
Improvement Decision
  ↓
Improvement Application
  ↓
Verification / Rollback
  ↺ Feedback
```

## Verification
Focused verification covers canonical type enforcement, consumed-source enforcement, distinct identity, explicit metadata, lineage rechecks, immutable candidate evidence, source non-mutation, recursive freezing, rejection behavior, and authority-boundary walls.

Local verification completed:

```text
28 focused tests: PASS
57 focused + regression tests: PASS
2708 core tests: PASS
```
