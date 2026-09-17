# Security Architecture

Phase 4 places a provider-neutral security control plane around the growing capability system.

```text
Principal / Session
      ↓
Permission Grant
      ↓
Opaque Secret Reference (when required)
      ↓
Capability Isolation Profile
      ↓
Trust / Risk Assessment
      ↓
Security Admission
      ↓
Tamper-Evident Audit Evidence
      ↓
Security Verification
      ↓
Recovery Proposal
      ↓
existing Authority Boundary
      ↓
existing Execution Boundary
```

## Identity

Security requests bind to a concrete authenticated session and principal identity. Identity describes who is asking; it does not grant permission by itself.

## Permission

Permissions are explicit principal/capability/action grants. A grant is not execution and is not a substitute for the existing JARVIS authority pipeline.

## Secrets

The security domain uses opaque secret references only. Raw secret values are intentionally absent from security contracts and serialized context.

## Isolation

Each protected capability can be bound to an isolation profile controlling network access, filesystem operations, subprocess use, allowed paths/hosts, and duration.

## Trust

Trust is derived from explicit evidence and evaluated against a deterministic policy. It is a security signal, not certainty or truth.

## Audit

Admission events form an append-only hash chain. The chain is tamper-evident and remains in-memory until a future persistence phase supplies a durable store.

## Recovery

Security verification can produce a bounded recovery proposal such as reauthentication, permission review, secret-reference rotation, capability quarantine, or audit investigation. The security layer does not apply the recovery automatically.

## Boundary

`SecuritySystem` can be composed into `JarvisRuntime` for inspection and protection, while runtime authority flags remain unchanged: security does not authorize or execute capabilities.
