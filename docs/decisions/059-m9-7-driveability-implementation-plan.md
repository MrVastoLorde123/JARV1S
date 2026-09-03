# Decision 059 — M9.7 Driveability Implementation Plan

## Status

Accepted — implementation starts from the M9.6 verified boundary.

## Initial implementation shape

M9.7 introduces an immutable objective/continuation contract and a deterministic controller before any model-driven next-step selection.

The implementation establishes:

- explicit objective identity and lifecycle state
- bounded continuation cycles
- stable cycle/provenance identity
- deterministic stop reasons
- next-step proposals that are non-executing
- handoff points into existing delegation/agency boundaries
- explicit objective cancellation/completion semantics

The controller must not execute actions, create authorization, mutate policy, expand worker capability, or bypass M7–M9.6.

## Design principle

Build the driveability boundary first. Intelligence may improve proposal quality later, but safety and authority remain independent of model capability.
