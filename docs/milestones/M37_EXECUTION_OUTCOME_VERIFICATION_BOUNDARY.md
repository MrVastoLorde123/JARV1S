# M37 — Execution Outcome / Verification Boundary

## M37.1 Outcome classification
Classify M36 controlled-agency results into bounded `NOT_ATTEMPTED`, `SUCCEEDED`, `FAILED`, or `BLOCKED` outcomes without treating observation as verification.

## M37.2 Verification input
Provide an immutable `VerificationInput` contract for an existing independent verifier.

## M37.3 Verification decision
Represent `PENDING`, `VERIFIED`, `REJECTED`, and `BLOCKED` decisions. `VERIFIED` requires evidence identity.

## M37.4 Authority separation
No authorization creation, execution, provider invocation, or verification-evidence manufacture is introduced.

## M37.5 Verification gate
Focused tests, source contract gate, UI build, and full core regression remain the milestone exit conditions.
