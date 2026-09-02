# Decision 036 — Proposed Consequence Semantics

## Status

M7.4 — Proposed Consequences

## Decision

JARVIS reasoning may produce action-shaped proposals, but proposals are never
authorization, execution requests, tool invocations, or executable payloads.

The proposal boundary sits after interpretation and prioritization:

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
Deterministic validation
    ↓
Policy / confirmation / execution
```

## Rules

1. A proposal belongs to exactly one reasoning request.
2. A proposal may describe a consequence and its kind: answer, ask,
   investigate, prepare, defer, or plan.
3. Proposals may reference the priority target or reasoning artifacts that
   motivated them.
4. A proposal has no authority field that can grant permission.
5. Proposal metadata cannot contain authorization, execution, or tool-handle
   controls.
6. Proposal serialization explicitly identifies the epistemic role as
   `proposed` and records authorization as false.
7. Validation may reject malformed or out-of-bound proposals, but validation
   still does not authorize execution.
8. Conflicts should generally produce investigation proposals; missing
   information should generally produce ask proposals.

## Non-goals

M7.4 does not select tools, build executable arguments, invoke providers,
authorize actions, request confirmation, or execute anything.

## Rationale

This keeps the reasoning system useful enough to recommend what should happen
next while preserving the deterministic safety boundaries established by the
execution architecture.
