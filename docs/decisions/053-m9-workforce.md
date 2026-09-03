# Decision 053 — M9 Workforce / Delegation

## Status

Accepted — M9 active.

## Decision

M9 extends M8 controlled agency into bounded workforce and delegation. Workers are execution/reasoning participants with explicit identity, assignment, capability, context, and reporting bounds. Workers never become a second authority system.

## Roadmap

- M9.1 — Worker Identity / Assignment Boundary
- M9.2 — Bounded Worker Runtime
- M9.3 — Worker Context / Knowledge Boundary
- M9.4 — Worker Reporting / Result Integration
- M9.5 — Delegation / Coordination
- M9.6 — Workforce Reliability / Recovery
- M9.7 — Driveability / Objective Continuation

## Core invariants

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Worker Context ≠ Global Context
Worker Output ≠ Truth
Delegation ≠ Authority Escalation
Objective Continuation ≠ Authorization
```

## Authority rule

JARVIS may distribute work without distributing authority. Every executable action remains on the established M7 → M8 path and must arrive as an authority-bearing M7 `ExecutionPreparation` before execution.
