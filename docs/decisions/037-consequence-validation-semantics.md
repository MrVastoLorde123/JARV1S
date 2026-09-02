# Decision 037 — Consequence Validation Semantics

## Status

M7.5 — Consequence Validation

## Decision

JARVIS proposals must pass a deterministic validation boundary before they
are eligible for policy evaluation. Validation establishes structural and
semantic validity only; it never grants authorization, selects tools, invokes
providers, requests confirmation, executes actions, or mutates system state.

The boundary is:

```text
WorkingContext
    ↓
ReasoningContext
    ↓
Interpretation
    ↓
Prioritization
    ↓
Proposed Consequences
    ↓
Consequence Validation
    ↓
Policy / confirmation / execution
```

## Rules

1. Each validation belongs to exactly one reasoning request and one proposal ID.
2. Validation status is explicitly `valid` or `invalid`.
3. Validation violations are deterministic findings with a code, message, and severity.
4. An invalid validation must contain at least one error-severity violation.
5. A valid validation cannot contain an error-severity violation.
6. Proposal priority and support references must resolve against the supplied prioritization.
7. Authorization, execution, and tool-handle controls are validation failures when present.
8. Proposal serialization must retain the `proposed` epistemic role and explicit false authorization state.
9. Validation results are provider-neutral and deterministically serializable.
10. Validation never mutates the supplied proposal, reasoning context, prioritization, interpretation, or system state.
11. A failed validation is a terminal semantic result for the policy boundary; it must not be treated as valid input to policy or confirmation.
12. Validation confidence cannot override a deterministic failure.

## Collection Semantics

A proposal collection produces one deterministic validation result per proposal,
using stable proposal IDs in collection order (`proposal:0`, `proposal:1`, ...).
The collection exposes `all_valid` as a derived property rather than an
independent authorization decision.

## Non-goals

M7.5 does not evaluate policy, decide whether an action is permitted, discover
or select tools, build executable payloads, request user confirmation, or
execute anything.

## Rationale

Separating proposal generation from proposal validation prevents downstream
policy and execution layers from repairing or silently accepting malformed
semantic output. It creates a deterministic gate between reasoning and
authority while preserving the original proposal and its provenance.
