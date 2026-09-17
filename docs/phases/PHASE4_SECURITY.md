# Phase 4 — Security

## Objective

Protect the Phase 3 capability system with explicit identity, permissions, secret-reference handling, isolation, trust, auditability, security admission, verification, and bounded recovery.

## Architectural invariant

```text
Security ≠ Authorization
Security readiness ≠ Execution
Secret reference ≠ Secret value
Trust score ≠ Certainty
Audit evidence ≠ Truth
Recovery proposal ≠ Recovery application
```

The security layer may deny an unsafe request, but it never invokes a capability and never silently grants JARVIS authority.

## Milestones

| Checkpoint | Boundary | Primary result |
|---|---|---|
| M74 | Security Identity | explicit principal + session identity |
| M75 | Permission Model | capability/action grants bound to principals |
| M76 | Secret Reference Boundary | opaque, non-exporting secret references |
| M77 | Capability Isolation | deterministic resource/network/subprocess bounds |
| M78 | Trust / Risk | evidence-backed security risk assessment |
| M79 | Audit Evidence | append-only hash-chained security evidence |
| M80 | Security Admission | combined security gate before downstream action |
| M81 | Verification / Recovery | exact-evidence verification + non-applied recovery proposal |
| M82 | Security System | aggregate security control plane + runtime seam |

## Scope exclusions

This phase does not add external AI providers, credential retrieval, subprocess execution, external persistence, automatic secret rotation, permission mutation, or execution dispatch.

## Completion gate

The phase closes only after:

1. focused Phase 4 tests pass;
2. the Phase 4 static contract verifier passes;
3. the UI production build passes;
4. the full `src.core.tests` regression baseline remains 3279/3279.
