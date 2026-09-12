# 016 — Authority Handoff Boundary

## Status

Proposed implementation boundary for M31.

## Purpose

M31 establishes the boundary between **evidence-gated consequence eligibility** and the existing **authority/confirmation system**.

The core rule is:

> Eligibility can prepare an authority handoff. Eligibility never becomes authorization.

M30 answers whether a bounded consequence is evidence-eligible. M31 packages that result, with its provenance and authority context, into a deterministic handoff record that a separate authority layer may evaluate.

## Dispositions

M31 defines three handoff statuses:

```text
READY_FOR_AUTHORITY
REQUIRE_REVIEW
BLOCKED
```

The mapping is deterministic:

```text
M30 ALLOW             -> READY_FOR_AUTHORITY
M30 REQUIRE_REVIEW    -> REQUIRE_REVIEW
M30 BLOCK              -> BLOCKED
```

`READY_FOR_AUTHORITY` means only that the M30 evidence gate has been satisfied and the request is structurally ready to be considered by a separate authority layer.

## Provenance

The handoff preserves:

- claim identity
- task identity
- consequence kind
- consequence identity
- consequence metadata
- authority target
- authority context
- evidence references
- verification references
- deterministic handoff identity

The handoff therefore does not sever the M29 evidence chain.

## Inertness

M31 cannot:

- authorize a tool or workflow
- invoke a tool
- call a confirmation provider
- bypass confirmation
- mutate policy
- grant permissions
- execute a consequence
- transform `READY_FOR_AUTHORITY` into authorization by itself

The existing policy and confirmation layers remain the authority boundary. The generic policy layer distinguishes whether confirmation is required, while the confirmation provider obtains or denies confirmation. M31 only prepares the handoff between those layers and the evidence/consequence system.

## Service integration

`CodingAgentService.prepare_authority_handoff()` provides the narrow seam from M30 consequence decisions to the M31 handoff object.

The service method is pure with respect to execution: it creates a handoff record and performs no authority operation.

For coding workflows, `authority_context` can carry an existing operation identifier or other authority-specific context without making M31 aware of the underlying permission mechanism.

## Explicit non-goals

M31 does not introduce:

- automatic execution
- automatic confirmation
- new permission semantics
- peer-agent approval
- dispute resolution
- persistent authority records
- resource scheduling
- a second confirmation system

Those remain separate future boundaries or existing authority mechanisms.
