# M22.4 — Capability Permission / Policy Binding Boundary

## Purpose

M22.4 establishes a bounded declarative permission/policy binding layer for JARVIS capabilities.

A binding answers which named permission is allowed or denied for a capability identity, under which policy identity, and optionally for which capability version. It is policy metadata, not authorization.

## Contract

```text
Capability Descriptor
        ↓
Provenance / Trust
        ↓
Version / Lifecycle
        ↓
Permission Binding
        ↓
Policy Context
        ↓
Validation / Policy Decision
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

M22.4 stops at declarative permission/policy binding.

## Core types

- `CapabilityPermissionBinding` — immutable capability/version/permission/policy binding.
- `PermissionEffect` — bounded `ALLOW` or `DENY` effect.
- `CapabilityPolicyBindingRegistry` — explicit, conflict-aware binding registry with deterministic lookup/listing.
- `CapabilityPolicyError` — bounded permission/policy contract error.

## Invariants

- Bindings require stable capability identity, permission name, effect, and policy identity.
- Permission names are normalized case/whitespace-insensitively.
- Optional versions use M22.3 Semantic Versioning normalization.
- Version-specific and version-agnostic bindings are distinct identities.
- Duplicate binding identities are rejected; an allow/deny conflict cannot silently overwrite another binding at the same identity.
- Binding objects are immutable.
- Registry lookup and listing are deterministic metadata operations.
- An `ALLOW` binding is declarative policy metadata and is not an authorization decision.
- A `DENY` binding does not itself cancel, revoke, or modify an existing authorization/execution record.
- Binding context explicitly records `permission_bound=True` while authority and authorization remain false.
- Policy-layer version validation converts lifecycle SemVer failures into the M22.4 `CapabilityPolicyError` boundary.

## Authority walls

```text
Permission Binding ≠ Authorization
Policy ≠ Authorization
ALLOW ≠ Authorized
DENY ≠ Execution Cancellation
Active ≠ Permission
Latest ≠ Authorized
Trust ≠ Permission
Permission ≠ Execution
```

## Deliberate exclusions

M22.4 does not authorize an invocation, confirm user intent, execute a plugin/capability, select or assign a worker, mutate policy through evaluation, infer trust from permission, convert `ALLOW` into an execution request, revoke an already-issued authorization, or bypass the existing validation/policy/confirmation/authorization/execution chain.

## Verification

Remote implementation status: **VERIFIED / COMPLETE**.

Local receipt: **9/9 M22.4 focused + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core tests passed locally.**
