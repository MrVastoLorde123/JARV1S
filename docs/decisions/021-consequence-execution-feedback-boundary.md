# Decision 021 — Consequence Execution Feedback Boundary

## Status

Proposed implementation boundary for M36.

M35 establishes an immutable observed execution outcome. M36 converts that observation into an immutable feedback event for later evaluation. M36 does not decide what the outcome means for learning, retry, truth, authority, or policy.

## Decision

Introduce `ConsequenceExecutionFeedbackService` as the M35 → M36 bridge.

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
M36 Consequence Execution Feedback
  ↓
Separate evaluation / learning / retry boundaries
```

## Contract

- `COMPLETED_SUCCESS` becomes `SUCCESS` feedback.
- `COMPLETED_FAILURE` becomes `FAILURE` feedback.
- `NOT_EXECUTED` becomes `NOT_EXECUTED` feedback.
- The feedback event preserves the complete M35 provenance chain.
- Execution result data is carried only as observed payload; M36 does not reinterpret it as truth.
- Blocked/not-executed outcomes never invent execution identifiers or results.
- Feedback identity is deterministic for the exact observed outcome.
- Feedback is immutable and observational.
- M36 never authorizes, executes, retries, revokes, mutates policy, writes learning state, mutates memory, or establishes semantic truth.

## Authority walls

```text
Outcome ≠ Feedback Evaluation
Feedback ≠ Learning Decision
Feedback ≠ Retry Authority
Feedback ≠ Truth Authority
Feedback ≠ Authorization
Feedback ≠ Execution
```

## Verification

Focused M36 tests, coding-service integration tests, M35 compatibility, full agents, and full core regression are required before VERIFIED / COMPLETE.
