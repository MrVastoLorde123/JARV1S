# 015 — Evidence-Gated Consequence Boundary

## Status

Proposed implementation boundary for M30.

## Purpose

M30 introduces the first deterministic boundary that consumes an M29 claim evaluation and determines whether a bounded workflow consequence is eligible to advance.

The boundary is epistemic-to-workflow governance. It is not an authorization system.

## Core rule

> Evidence can make a consequence eligible. Evidence never becomes authority.

A `VERIFIED` claim may satisfy the evidence requirement for a bounded consequence, but the resulting M30 decision must still pass through the existing JARVIS authority, confirmation, policy, and tool boundaries before any consequential action is executed.

## Consequence dispositions

M30 defines three deterministic dispositions:

```text
ALLOW
BLOCK
REQUIRE_REVIEW
```

`ALLOW` means only that the evidence requirement for the named consequence has been satisfied. It does not mean that execution is authorized.

## Initial consequence kinds

The first bounded consequence classes are:

- `ADVANCE_WORKFLOW`
- `MARK_COMPLETED`

Both require `VERIFIED` evidence.

The policy intentionally does not define a universal rule that `VERIFIED` unlocks every future consequence.

## State mapping

```text
PROPOSED      → BLOCK
UNKNOWN       → BLOCK
SUPPORTED     → REQUIRE_REVIEW
VERIFIED      → ALLOW
CONTRADICTED  → BLOCK
DISPUTED      → BLOCK
REJECTED      → BLOCK
```

The mapping is deterministic and consequence-specific.

## Inertness

The M30 boundary cannot:

- invoke tools
- authorize a tool
- grant permissions
- mutate policy
- change confirmation requirements
- execute a workflow consequence
- infer truth outside the M29 evaluation supplied to it

The returned decision is therefore a governance input to a later authority layer, not an execution command.

## Provenance

Every M30 decision preserves:

- claim identity
- task identity
- requested consequence identity
- M29 evidence references
- M29 verification references
- deterministic disposition and reason

This prevents the consequence layer from severing the evidence chain that justified the decision.

## Coding-agent integration

`CodingAgentService.decide_consequence()` provides the narrow service seam from M29 evaluation to M30 consequence eligibility.

The seam consumes a completed `ClaimEvaluation`; it does not execute the coding worker and does not bypass the existing execution authority boundary.

## Explicit non-goals

M30 does not introduce:

- peer-agent review
- dispute resolution workflows
- human escalation orchestration
- computational resource scheduling
- a persistent claim database
- automatic execution from `ALLOW`

Those remain separate architectural boundaries.
