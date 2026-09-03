# M9.3 — Worker Context / Knowledge Boundary

## Status

IMPLEMENTATION IN PROGRESS — verification pending.

## Goal

Define what a worker is allowed to know without exposing JARVIS's global working context by implication.

## Implemented

- `WorkerContext` is an immutable worker-scoped projection.
- `WorkerContextProjector` requires explicit `WorkerDefinition`, `WorkerAssignment`, and global `WorkingContext` inputs.
- Projection is restricted to the assignment's declared `input_scope`.
- Unsupported input-scope fields are rejected.
- Assignment/worker identity mismatch is rejected.
- Assignment bounds are revalidated before projection.
- Worker context serialization explicitly reports no authority grant and no global-context access.
- Knowledge access remains distinct from authorization.

## Boundary

```text
Worker Context ≠ Global Context
Knowledge Access ≠ Authority
Knowledge Access ≠ Permission
Projection ≠ Authorization
Worker Output ≠ Truth
```

The projector only exposes data already present in the global context. It does not retrieve additional data, mutate context, select providers, invoke tools, or grant authority.

## Verification

Focused target:

```text
python -m unittest src.agency.tests.test_worker_context -v
```

Full repository target:

```text
python -m unittest
```
