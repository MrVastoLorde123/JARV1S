# M7.3 — Prioritization Semantics

## Decision

Prioritization defines **attention ordering**, not action authority. Given a `ReasoningContext` and optional M7.2 `Interpretation`, JARVIS may determine what deserves attention first for the current request.

Prioritization may consider relevance, urgency, importance, apparent user intent, unresolved status, conflict, and execution state. These signals describe attention only.

## Contract

```text
ReasoningContext + Interpretation
            ↓
      PrioritizationProjector
            ↓
       Prioritization
            ↓
  ordered PriorityTarget values
```

Each target has an explicit `PrioritySignal` and deterministic score. Equal scores are ordered by target ID so the result is reproducible.

## Invariants

- Prioritization request must match the reasoning request.
- Priority targets are immutable and ranked contiguously from zero.
- Signals are bounded to `[0.0, 1.0]`.
- Higher attention score ranks first.
- Missing information, uncertainty, and conflicts can become attention targets.
- Execution state may affect attention but cannot authorize an action.
- Prioritization cannot execute tools, authorize actions, mutate memory/conversation, or replace policy/confirmation/execution boundaries.
- Priority score is never an authority score.
- Deterministic ordering must not depend on provider/model behavior.

## Non-goals

M7.3 does not choose tools, create executable plans, authorize actions, execute anything, or decide what should be persisted as memory.

## Weighting

The initial deterministic attention score is:

`0.25 relevance + 0.15 urgency + 0.15 importance + 0.15 user_intent + 0.10 unresolved + 0.10 conflict + 0.10 execution`

These weights are an implementation baseline, not a claim that human attention can be reduced to a universal formula. Later milestones may replace or extend the scoring mechanism while preserving the semantic boundary that prioritization is non-authoritative.
