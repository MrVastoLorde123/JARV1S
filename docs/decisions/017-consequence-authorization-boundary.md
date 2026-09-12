# Decision 017 — Consequence Authorization Boundary

## Status

Proposed implementation boundary for M32.

## Context

M31 converts an evidence-eligible M30 consequence into a provenance-preserving
`AuthorityHandoffRequest`. M31 deliberately stops before authorization.

JARVIS already has an explicit M22.8 authorization boundary built from the
existing policy and confirmation contracts. M32 must connect the newer
consequence authority chain to that existing authorizer without creating a
second policy system or allowing a consequence decision to execute a tool.

## Decision

Introduce `ConsequenceAuthorizationService` as the M31 → M22.8 bridge.

```text
M29 ClaimEvaluation
        ↓
M30 ConsequenceDecision
        ↓
M31 AuthorityHandoffRequest
        ↓
M32 ConsequenceAuthorizationService
        ↓
Existing ExplicitAuthorizationService
        ↓
AuthorizationDecision
        ↓
Separate execution boundary
```

M32 accepts only `READY_FOR_AUTHORITY` handoffs whose `authority_target`
matches the configured M32 target. The exact `ToolRequest` must carry the
M31 `authority_handoff_id` and matching `task_id`.

The existing `ExplicitAuthorizationService` remains the sole source of policy
and confirmation authorization. M32 wraps its result with M31 provenance in an
immutable `ConsequenceAuthorizationDecision`.

## Contract

- `READY_FOR_AUTHORITY` may enter authorization.
- `REQUIRE_REVIEW` and `BLOCKED` are denied without calling the underlying
  authorization service.
- A mismatched authority target is denied.
- A request not explicitly bound to the handoff is denied.
- A request with mismatched task lineage is denied.
- Existing policy denial remains denial.
- Existing confirmation denial remains denial.
- Explicit policy + confirmation approval produces `AUTHORIZED`.
- Authorization preserves handoff, claim, task, consequence, evidence, and
  verification provenance.
- Authorization is immutable and inspectable.
- M32 performs no tool invocation, no `ToolService` call, no policy mutation,
  no permission mutation, and no execution.

## Authority walls

```text
Evidence ≠ Eligibility
Eligibility ≠ Authority Handoff
Authority Handoff ≠ Authorization
Authorization ≠ Execution
Policy ≠ Authorization
Confirmation ≠ Execution
```

## Binding rule

The authorization request must carry:

```text
metadata.authority_handoff_id == handoff.handoff_id
metadata.task_id == handoff.task_id
```

This prevents an independently constructed tool request from borrowing a
consequence-level authorization decision.

## Deliberate exclusions

M32 does not:

- execute tools;
- replace `ExplicitAuthorizationService`;
- invent a new policy language;
- grant permission outside the existing policy + confirmation contracts;
- add authorization persistence or revocation;
- create execution records;
- bypass the existing `PolicyGate`/tool execution boundary.

## Verification

The milestone requires focused M32 contract tests, M31/M30/M29 compatibility
suites, the complete `src.agents.tests` suite, and the full `src.core.tests`
regression before it is considered VERIFIED / COMPLETE.
