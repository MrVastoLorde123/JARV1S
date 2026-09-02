# Decision 038 — Policy Input Semantics

## Status

M7.6 — Policy Input Semantics

## Decision

Policy evaluates a canonical, validated policy input derived from a validated
proposed consequence and its deterministic validation result. Policy does not
consume raw model output, arbitrary WorkingContext, or an unvalidated proposal.

## Rules

1. Policy input belongs to exactly one reasoning request.
2. The referenced proposal and validation result must belong to that request.
3. The policy input records only authority-relevant facts needed for policy evaluation.
4. Action characteristics are descriptive, not authorization decisions.
5. Validation status is explicit and must be VALID before a policy input can be constructed.
6. Provenance identifies the proposal and validation artifacts used to construct the input.
7. Policy input contains no tool handle, executable payload, confirmation result, or authorization grant.
8. Construction is deterministic and non-mutating.
9. A valid policy input does not itself authorize execution.

## Non-goals

M7.6 does not evaluate policy, authorize actions, request confirmation, select
tools, invoke providers, or execute anything.

## Rationale

A narrow policy boundary prevents policy evaluation from becoming an implicit
second reasoning engine. It gives policy a stable, inspectable input while
keeping interpretation, proposal generation, validation, authorization,
confirmation, and execution as distinct responsibilities.
