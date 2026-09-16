# M23.414–415 — Capability Realization Boundary Hardening

## Decision

Harden the composition boundary between capability selection and validated tool-request preparation.

### M23.414 — Realization Integrity

`CapabilityRealization` now validates its own runtime contract:

- intent is a non-empty string
- selection is a `CapabilitySelection`
- candidate is a `CapabilityCandidate`
- request is a `ToolRequest`
- candidate must originate from the selection snapshot
- request tool identity must match the selected capability

The realization remains frozen and does not invoke tools, authorize execution, interpret confirmation, or establish verification truth.

### M23.415 — Boundary Test Coverage

Focused tests cover malformed realization fields, candidate provenance, request/candidate identity mismatch, frozen-instance behavior, and preservation of the non-executing boundary.

## Invariants

```text
Selection ≠ Execution
Candidate provenance ≠ Authorization
Validated request ≠ Permission
Capability realization ≠ Tool invocation
Frozen result ≠ Verification truth
```

## Verification

User-local verification should be batched with the existing core and tools regressions after the bulk boundary changes.
