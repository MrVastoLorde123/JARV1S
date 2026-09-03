# M9.1 — Worker Identity / Assignment Boundary

## Status

IMPLEMENTATION COMPLETE — verification pending from the user's real checkout.

## Scope

M9.1 establishes the immutable workforce contracts required before worker execution exists.

Implemented contracts:

- `WorkerDefinition`
- `WorkerAssignment`
- `WorkerReport`
- `WorkerReportStatus`
- `WorkerRegistry`

## Invariants

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Worker Context ≠ Global Context
Worker Output ≠ Truth
Delegation ≠ Authority Escalation
```

A worker definition provides stable identity and hard bounds. An assignment describes requested work and may be rejected when it exceeds the registered worker's capability or step bounds.

Assignments and reports serialize without authority grants. Metadata cannot contain authority, execution, provider, or credential controls.

## Verification target

```text
python -m unittest src.agency.tests.test_workforce -v
python -m unittest
```

## Next

M9.2 adds bounded worker execution while retaining the M7 → M8 authority and execution path.
