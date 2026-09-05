# Decision 012 — Capability Request Proposal Boundary

**Status:** Accepted

## Context

M22.6 established an immutable discovery-plus-selection snapshot. The repository
also contains a structural `CapabilityInvocationBuilder` and replaceable
argument-planning contract, but selection must not be allowed to silently turn
into an execution request.

JARVIS needs a narrow bridge that can transform a selected capability and
proposed arguments into a structurally validated `ToolRequest` while preserving
the authority chain.

## Decision

Introduce `CapabilityRequestProposalService` and
`CapabilityRequestProposal` as the boundary between capability selection and
the existing tool validation/invocation stack.

```text
CapabilityDiscoverySelection
        ↓
CapabilityRequestProposalService
        ↓
CapabilityArgumentPlanner
        ↓
CapabilityInvocationBuilder
        ↓
CapabilityRequestProposal
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Sandbox
        ↓
Execution
```

The proposal service must only accept capabilities originating from the same
M22.6 discovery/selection snapshot. The argument planner may be deterministic,
model-backed, or another provider implementing the same contract; it may only
propose data.

The invocation builder performs structural validation against the declared
input schema and materializes an inert `ToolRequest`. It does not invoke the
capability and does not decide policy, confirmation, or authorization.

## Constraints

- `Selection ≠ Request Authorization`
- `Argument Proposal ≠ Execution`
- `Validated ToolRequest ≠ Authorized ToolRequest`
- `ToolRequest ≠ Tool Execution`
- `Capability ≠ Worker`
- `Permission ≠ Authorization`
- `Sandbox ≠ Authorization`
- A proposal must be traceable to the exact discovery/selection snapshot.
- No service introduced by this decision may call a tool gateway, policy gate,
  confirmation provider, authorization component, or sandbox runner.

## Consequences

Positive:

- The model/selector can produce useful structured proposals without gaining
  execution authority.
- Argument generation remains replaceable and testable.
- Structural request validation is deterministic and independent from policy.
- The existing `PolicyGate` remains the execution boundary.

Trade-off:

- M22.7 does not perform authorization or execution. Those remain explicit
  downstream boundaries and require their own milestones and receipts.
