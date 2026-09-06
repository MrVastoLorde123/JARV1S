# Decision 109 — Learning-State Evidence V4

## Status
VERIFIED / COMPLETE

## Parent
`f4a33d6910ab2fdd8ecc7b44a4341b6a4e24e4e6` — M23.96 Application Learning Adaptation Application Integrity V4.

## Purpose
M23.97 establishes an explicit evidence boundary for a potential future durable learning-state transition.

The boundary consumes application-integrity evidence and emits immutable learning-state evidence only when the upstream application is `APPLIED` and its integrity is `VALID`. It does not persist state or invoke learning.

## Contract
- Consumes exactly one M23.96 application-integrity v4 artifact.
- Requires a non-empty evidence identity.
- Emits `READY` only when application status is `APPLIED` and application-integrity status is `VALID`.
- Emits `BLOCKED` for any upstream application or integrity state that is not eligible for learning-state evidence.
- Preserves application, integrity, decision, proposal, eligibility, signal, evaluation, feedback, classification, source-integrity, source-decision, outcome, status, confidence, and application fingerprints.
- Carries bounded evidence metadata supplied by the caller and recursively freezes evidence, reasons, and lineage.
- Preserves the source artifact without mutation.
- `READY` evidence cannot carry a failure reason; `BLOCKED` evidence must carry one.

## Authority walls
Learning-state evidence is not durable learning state, learner invocation, memory mutation, model mutation, policy mutation, persistence, authorization, truth, scheduling, or execution.

`Learning-State Evidence ≠ Learning`
`Learning-State Evidence ≠ Persistence`
`Learning-State Evidence ≠ Authorization`
`Learning-State Evidence ≠ Truth`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → (future durable learning-state transition)`

M23.97 deliberately stops before persistence, learner invocation, model update, memory mutation, policy mutation, retry, scheduling, authorization, or execution.

## Verification
Focused verification: **14/14**.
Core regression: **1528/1528**.

The focused suite contains fourteen tests covering READY formation, provenance, fingerprint preservation, recursive immutability, source preservation, invalid-integrity blocking, non-applied blocking, wrong-source rejection, blank-ID rejection, enum validation, READY/BLOCKED failure-reason invariants, and advisory/mutation walls.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.96.
