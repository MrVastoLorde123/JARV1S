# Phase 4 Decision — Security

## Decision

Harden the capability system with an explicit, provider-neutral security control plane before introducing external intelligence providers.

## Checkpoints

- M74 — Security Identity
- M75 — Permission Model
- M76 — Secret Reference Boundary
- M77 — Capability Isolation
- M78 — Trust / Risk Model
- M79 — Tamper-Evident Audit Evidence
- M80 — Security Admission
- M81 — Security Verification / Recovery
- M82 — Security System + Runtime Boundary

## Security chain

```text
Identity
  ↓
Permission
  ↓
Opaque Secret Reference
  ↓
Capability Isolation
  ↓
Trust / Risk
  ↓
Security Admission
  ↓
Audit Evidence
  ↓
Security Verification
  ↓
Recovery Proposal
```

Security is a protection boundary, not a replacement for JARVIS authority. A security-admitted request is not automatically authorized or executed. The existing deterministic authority and execution boundaries remain responsible for those decisions.

## Secret policy

Raw secret material does not enter the security domain. Security stores only opaque references, ownership, capability scope, sensitivity, and version metadata.

## Recovery policy

Security recovery is deliberately proposal-only in this phase. Reauthentication, permission review, secret-reference rotation, capability quarantine, and audit investigation are represented as bounded decisions; the security layer does not silently apply them.

## Audit policy

Security decisions produce append-only, hash-chained evidence in the in-memory audit boundary. External persistence is outside this phase.
