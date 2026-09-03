# Decision 053 — M9 Workforce / Delegation Architecture

## Status

Accepted — 2026-09-03

## Decision

M9 extends M8 controlled agency with bounded worker actors and delegation while preserving one authority system.

The canonical workforce flow is:

```text
M7 Authority
    ↓
Agency
    ↓
Worker Assignment
    ↓
Bounded Worker
    ↓
M8 Execution
    ↓
Observation
    ↓
Worker Report
    ↓
Agency / Context
```

Workers do not create authority. An assignment is a work envelope, not an authorization grant. Capability bounds, context bounds, output bounds, and step limits are explicit and immutable contracts.

## M9 boundaries

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Worker Context ≠ Global Context
Worker Output ≠ Truth
Delegation ≠ Authority Escalation
```

Every executable worker action must remain an existing M7 `ExecutionPreparation` and pass through M8 execution semantics.

## M9 roadmap

- M9.1 — Worker Identity / Assignment Boundary
- M9.2 — Bounded Worker Runtime
- M9.3 — Worker Context / Knowledge Boundary
- M9.4 — Worker Reporting / Result Integration
- M9.5 — Delegation / Coordination
- M9.6 — Workforce Reliability / Recovery
- M9.7 — Driveability / Objective Continuation

Driveability is therefore an objective-level capability built after the worker and delegation foundations, not an implicit authority granted to individual workers.

## M9.1

`WorkerDefinition`, `WorkerAssignment`, `WorkerReport`, and `WorkerRegistry` establish stable identity and explicit bounds. Capability escalation is rejected at the worker acceptance/registry boundary rather than being mistaken for structural invalidity of an assignment request.

## M9.2

`BoundedWorkerRuntime` consumes valid M9.1 assignments and routes execution through `ControlledAgency` and `ExecutionRuntime`. Provider-neutral operation names are resolved to capability identities through an explicit resolver; worker code never assumes operation names are capability names.

No dynamic capability acquisition, worker-created authorization, provider bypass, or hidden retry is permitted.
