# Decision 120 — Learning-State Interpretation Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`99ba4d9566a396a7c1e5f851ed7571fbd31e75b0` — M23.107 Learning-State Interpretation Request Boundary.

## Purpose
M23.108 establishes the first bounded semantic interpretation step after an accepted learning-state interpretation request.

A `READY` M23.107 request may be passed to one caller-supplied interpreter adapter. The boundary records the adapter's returned mapping as an immutable interpretation artifact and preserves the full request provenance. The boundary does not decide whether the interpretation is true, correct, useful, certain, actionable, learnable, authoritative, or executable.

## Contract
- Consumes exactly one canonical `LearningStateInterpretationRequest` artifact.
- Requires request status `READY`.
- Requires a non-empty interpretation identity.
- Requires a callable interpreter adapter.
- Invokes the interpreter at most once for one request operation.
- Supplies only the request's frozen state payload to the interpreter.
- Accepts only a mapping result as a completed interpretation.
- Converts interpreter exceptions and non-mapping results into a bounded `REJECTED` interpretation artifact.
- Preserves request, read-validation, read, consumption-request, source-validation, integrity, transition, evidence, application, state-key, and fingerprint identities.
- Preserves interpretation output as recursively frozen evidence.
- Emits immutable reasons and lineage.
- Does not infer semantic meaning itself; the semantic transformation is delegated to the injected interpreter.
- Does not invoke a learner, update a model, mutate memory or policy, grant authority, schedule work, or execute action.
- Repeated construction from equivalent request evidence and equivalent interpreter output is deterministic.

## Authority Walls
`Interpretation ≠ Truth`
`Interpretation ≠ Correctness`
`Interpretation ≠ Certainty`
`Interpretation ≠ Learning`
`Interpretation ≠ Model Update`
`Interpretation ≠ Memory Mutation`
`Interpretation ≠ Authorization`
`Interpretation ≠ Permission`
`Interpretation ≠ Policy Mutation`
`Interpretation ≠ Planning`
`Interpretation ≠ Execution`
`Interpreter Capability ≠ Interpreter Authority`
`Interpretation Request ≠ Interpretation`

M23.108 only records a bounded semantic result produced by an injected interpreter. Any later claim about truth, usefulness, learning, authority, or action requires a separate boundary.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → (future interpretation validation)`

M23.108 therefore establishes a semantic transformation without collapsing transformation into validation, belief, learning, or authority.

## Verification Plan
Focused tests cover accepted-request gating, rejected-request gating, wrong-source rejection, interpretation identity gating, exactly-one interpreter invocation, interpreter exception handling, non-mapping result handling, provenance/fingerprint preservation, recursive interpretation immutability, source preservation, deterministic construction, semantic ownership by the injected interpreter, and absence of truth/learning/authority/execution powers.

Verified locally:
- Focused verification: **15/15**.
- Core regression: **1637/1637**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.107.
