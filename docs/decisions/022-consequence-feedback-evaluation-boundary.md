# Decision 022 — Consequence Feedback Evaluation Boundary

## Status

Proposed implementation boundary for M37.

M36 establishes immutable consequence execution feedback. M37 classifies that feedback into an inert evaluation signal for a later learning decision. M37 does not write learning state, mutate memory, authorize retry, execute tools, establish truth, or grant authority.

## Decision

Introduce `ConsequenceFeedbackEvaluationService` as the M36 → M37 bridge.

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
M37 Consequence Feedback Evaluation
  ↓
Separate learning decision / learning write / retry boundaries
```

## Contract

- `SUCCESS` feedback becomes `SUCCESS_SIGNAL`.
- `FAILURE` feedback becomes `FAILURE_SIGNAL`.
- `NOT_EXECUTED` feedback becomes `NOT_EXECUTED_SIGNAL`.
- The complete consequence provenance chain is preserved.
- Evaluation is deterministic and immutable.
- Confidence is an evaluation field, not authority or truth.
- `NOT_EXECUTED` never invents an execution identifier.
- Evaluation evidence is observational and may be consumed by a later learning decision boundary.
- M37 never writes learning state, mutates memory, authorizes retry, executes tools, revokes capability, mutates policy, or establishes semantic truth.

## Authority walls

```text
Feedback ≠ Evaluation
Evaluation ≠ Learning Decision
Evaluation ≠ Learning Write
Evaluation ≠ Retry Authority
Evaluation ≠ Truth Authority
Evaluation ≠ Authorization
Evaluation ≠ Execution
```

## Verification

Focused M37 tests, M36 compatibility, full agents, and full core regression are required before VERIFIED / COMPLETE.
