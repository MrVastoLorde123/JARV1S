# Decision 054 — M9.2 Bounded Worker Runtime

## Status

Accepted — 2026-09-03

## Decision

Workers become executable only through an explicit bounded runtime layered on the M9.1 worker/assignment contracts.

A worker run requires:

1. A registered `WorkerDefinition`.
2. A valid `WorkerAssignment` accepted by the `WorkerRegistry`.
3. An explicitly scoped `WorkingContext` supplied by the caller.
4. An existing M7 `ExecutionPreparation` with `READY` status.
5. Execution through the existing M8 `ControlledAgency` and `ExecutionRuntime`.

## Capability semantics

M7 `ExecutionRequest.operation` remains provider-neutral. M9.2 therefore resolves operation → capability through an injected resolver and checks the resolved capability against the assignment's allowed capability set.

Workers do not infer capability ownership and do not acquire new capabilities dynamically.

## Bounds

Worker execution is bounded by:

```text
min(worker.max_steps, assignment.max_steps)
```

Every subsequent worker preparation is checked against the same assignment capability envelope before it can reach M8 execution.

## Authority boundary

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Execution ≠ Authorization
Worker Output ≠ Truth
```

M9.2 does not create authorization, mutate policy, select providers independently, or invoke execution outside the M8 runtime.
