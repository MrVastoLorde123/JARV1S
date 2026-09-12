# Decision 024 — Consequence Learning Write Request Boundary

## Status

Proposed implementation boundary for M39.

M38 establishes deterministic learning eligibility. M39 converts only an eligible learning decision into a provenance-complete learning-write request. M39 does not persist learning state.

## Contract

- Only `LEARNING_ELIGIBLE` decisions may produce a write request.
- `REVIEW_REQUIRED` and `NOT_ELIGIBLE` decisions are rejected and cannot create a write request.
- The request preserves the complete consequence provenance chain.
- The request contains an immutable learning payload and deterministic request identity.
- The request explicitly carries the M38 confidence and evidence.
- The request is advisory to the later learning-state writer; it is not itself a persisted learning mutation.
- No retry, authorization, execution, revocation, policy mutation, or truth authority is created.

## Authority walls

```text
Learning Eligibility ≠ Learning Write
Learning Write Request ≠ Persisted Learning State
Learning Write Request ≠ Retry Authority
Learning Write Request ≠ Authorization
Learning Write Request ≠ Truth
```

## Verification

Focused M39 tests, M38 compatibility, full agents, and full core regression are required before VERIFIED / COMPLETE.
