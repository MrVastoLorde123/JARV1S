# M56 — Authorized Execution Outcome Bridge

## Scope

M56 closes the boundary between the exact M55 authorized runtime result and
the existing M37 outcome/verification-input substrate.

## Invariant

One M55 runtime admission produces one M37 `AgencyExecutionOutcome` and one
bounded `VerificationInput`, all retaining the exact execution identity and
request identity of the admitted path.

## Explicit non-responsibilities

M56 does not create authority, authorize work, request execution, execute work,
choose a provider/tool, verify the world, or derive recovery.

## Verification

Focused M56 tests, static contract verifier, UI build, and the full core test
baseline are required before M56 is considered locally verified.
