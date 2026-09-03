# M9.2 — Bounded Worker Runtime

## Status

IMPLEMENTATION IN PROGRESS — verification pending from the user's real checkout.

## Scope

`BoundedWorkerRuntime` executes work only after an M9.1 assignment has been validated and an M7 `ExecutionPreparation` is already `READY`.

Every worker step is routed through the existing M8 `ControlledAgency` and `ExecutionRuntime` path. The worker runtime does not create authorization, select providers, acquire credentials, or bypass the existing execution boundary.

## Capability boundary

M7 execution operations are provider-neutral. M9.2 therefore uses an explicit operation → capability resolver rather than assuming an operation string is itself a capability name.

The resolved capability must remain inside `WorkerAssignment.allowed_capabilities`.

## Bounds

The effective worker step limit is:

```text
min(WorkerDefinition.max_steps, WorkerAssignment.max_steps)
```

Subsequent provider-supplied preparations are revalidated against the assignment capability envelope.

## Reporting

Worker completion, failure, partial completion, and blocked starts produce immutable `WorkerReport` data. Reports carry worker/assignment identity but grant no authority and make no truth guarantee.

## Invariants

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Delegation ≠ Authority Escalation
Worker Output ≠ Truth
```
