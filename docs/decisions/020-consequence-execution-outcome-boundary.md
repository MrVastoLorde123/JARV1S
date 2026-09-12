# Decision 020 — Consequence Execution Outcome Boundary

## Status

Proposed implementation boundary for M35.

M34 stops at an explicit execution attempt. M35 converts that attempt into an immutable observed consequence outcome without creating retry, learning, authorization, or truth authority.

## Decision

Introduce `ConsequenceExecutionOutcomeService` as the M34 → M35 bridge.

```text
M29 Claim / Evidence
  ↓
M30 Consequence Eligibility
  ↓
M31 Authority Handoff
  ↓
M32 Authorization
  ↓
M33 Execution Preparation
  ↓
M34 Execution Attempt
  ↓
M35 Consequence Execution Outcome
  ↓
Separate feedback / learning / retry boundaries
```

## Contract

- `ATTEMPTED_COMPLETED` becomes `COMPLETED_SUCCESS`.
- `ATTEMPTED_FAILED` becomes `COMPLETED_FAILURE`.
- `BLOCKED` becomes `NOT_EXECUTED`.
- Successful outcomes require a successful execution result.
- Failed outcomes preserve the attempt failure reason.
- Blocked outcomes never invent an execution result.
- Full upstream provenance is preserved.
- Outcome derivation is deterministic, immutable, and observational.
- M35 never authorizes, executes, retries, revokes, mutates policy, writes learning state, or establishes semantic truth.

## Authority walls

```text
Eligibility ≠ Authorization
Authorization ≠ Preparation
Preparation ≠ Attempt
Attempt ≠ Outcome Interpretation
Outcome ≠ Learning
Outcome ≠ Retry Authority
Outcome ≠ Truth Authority
```

## Verification

Focused M35 tests, coding-service integration tests, M34 compatibility, full agents, execution-attempt tool coverage, and full core regression are required before VERIFIED / COMPLETE.
