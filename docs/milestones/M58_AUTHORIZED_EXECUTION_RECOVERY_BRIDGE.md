# M58 — Authorized Execution Recovery Bridge

## Scope

M58 closes the boundary between the exact M57 authorized execution
verification and the existing M38 bounded recovery substrate.

## Invariant

One M57 verification produces one M38 recovery decision for the supplied,
identity-matching objective and continuation cycle.

## Explicit non-responsibilities

M58 does not create authority, authorize work, request execution, execute work,
choose a provider/tool, verify the world, or redefine recovery policy.

## Verification

Focused M58 tests, static contract verifier, UI build, and the full core test
baseline are required before M58 is considered locally verified.
