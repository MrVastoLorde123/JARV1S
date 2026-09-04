# M14.1 — Context State

## Goal

Define a bounded immutable representation of currently relevant personal world-model state.

## Boundary

`ContextState` is a structured snapshot. It records state and provenance references for later context reasoning, but it does not establish truth, intent, policy, authorization, or execution permission.

## Invariants

- Context State ≠ Truth
- Context State ≠ Fact
- Context State ≠ User Intent
- Context State ≠ Policy
- Context State ≠ Authorization
- Context State ≠ Execution
- Observation ≠ Certainty
- Source Reference ≠ Authority
- Context updates return new immutable values rather than mutating prior state.

## Contract

- Context identity is bounded and explicit.
- State is JSON-like and defensively frozen.
- Source references are unique and bounded.
- Optional observation time is validated as ISO-8601 text.
- Serialization is deterministic and JSON-compatible.
- Serialization exposes explicit non-authority flags.

## Not included

Temporal history, goal/project context, situational context, cross-domain relevance, world-model reasoning, inference, proactive agency, and runtime context injection remain later M14 slices.
