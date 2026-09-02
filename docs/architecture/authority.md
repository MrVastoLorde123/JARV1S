# JARVIS Authority Architecture

## Purpose

JARVIS separates intelligence from authority.

A model may interpret, rank, propose, and explain. It does not thereby gain permission to act. Authority is established deterministically outside the model and culminates in a provider-neutral execution handoff.

## Authority Pipeline

```text
WorkingContext
      ↓
ReasoningContext
      ↓
Interpretation
      ↓
Prioritization
      ↓
Proposed Consequence
      ↓
Consequence Validation
      ↓
Policy Evaluation
      ↓
Confirmation (when required)
      ↓
Confirmation Integrity
      ↓
Authorization
      ↓
Authorization Integrity
      ↓
Execution Preparation / Handoff
```

## Semantic Walls

```text
Interpretation ≠ Truth
Validation ≠ Authorization
Confirmation ≠ Authorization
Authorization ≠ Execution
Integrity ≠ Authority
READY ≠ EXECUTED
```

These are architectural invariants, not suggestions.

## Identity Chain

```text
proposal_id
    ↓
validation_id
    ↓
policy_decision_id
    ↓
confirmation_id       (when required)
    ↓
authorization_id
    ↓
execution_id
```

Each stage gets its own identity so downstream records cannot silently masquerade as upstream decisions.

## M7 Boundary

M7 ends at `ExecutionPreparationStatus.READY`.

A `READY` execution request means that the action has passed the deterministic authority chain and is eligible for a downstream execution system. It does not mean the action has been invoked, completed, or succeeded.

M7 performs no provider invocation, tool selection, credential access, external side effect, or execution-state mutation.

## Why This Exists

The purpose of the authority layer is to make JARVIS capable of agency without allowing the intelligence layer to become an implicit authority layer.

This lets future execution adapters, plugins, workers, interfaces, and models evolve independently while preserving the same safety and provenance boundary.
