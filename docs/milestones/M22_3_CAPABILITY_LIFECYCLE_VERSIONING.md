# M22.3 — Capability Lifecycle / Versioning Boundary

## Purpose

M22.3 establishes bounded lifecycle and versioning semantics for registered capabilities.

The boundary answers:

- **Version identity:** which version of a capability is being described?
- **Lifecycle:** is that version active, deprecated, or retired?
- **History:** which versions exist, in deterministic order, and which version explicitly supersedes an older version?

Lifecycle/version metadata does not grant trust, permission, authorization, or execution rights.

## Contract

```text
Capability Descriptor
        ↓
Provenance / Trust
        ↓
Version Identity
        ↓
Lifecycle State
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

M22.3 stops at lifecycle and version metadata.

## Core types

- `SemanticVersion` — immutable Semantic Versioning precedence value.
- `CapabilityVersion` — immutable capability version identity and lifecycle metadata.
- `LifecycleStatus` — bounded lifecycle state: `ACTIVE`, `DEPRECATED`, or `RETIRED`.
- `CapabilityLifecycleRegistry` — explicit version history with deterministic lookup/order.
- `CapabilityLifecycleError` — bounded lifecycle/versioning contract error.

## Invariants

- Capability versions use `MAJOR.MINOR.PATCH` Semantic Versioning syntax, with optional prerelease/build metadata.
- Numeric prerelease identifiers cannot contain leading zeroes.
- Version precedence follows Semantic Versioning; build metadata does not change precedence.
- Registry ordering is deterministic even when versions have equal SemVer precedence through an explicit version-string tiebreaker.
- A capability version identity is immutable after creation.
- Duplicate capability/version identities do not silently replace one another.
- `supersedes`, when present, must reference an older version.
- Lifecycle changes are explicit and forward-only: `ACTIVE → DEPRECATED → RETIRED` or `ACTIVE → RETIRED`.
- A retired version cannot be reactivated.
- Transitioning lifecycle creates a new immutable value while preserving capability identity and version.
- Retired versions remain in history and may be explicitly included in queries.
- `latest()` is a metadata query; by default it excludes retired versions and does not select an authorized execution target.
- Lifecycle/version metadata is declarative and contains no executable behavior.

## Authority walls

```text
Version ≠ Identity Authority
Lifecycle ≠ Permission
Latest ≠ Authorized
Active ≠ Trusted
Deprecated ≠ Forbidden
Retired ≠ Deleted
Versioning ≠ Execution
Capability ≠ Permission
```

## Deliberate exclusions

M22.3 does not:

- execute a plugin or capability;
- grant permission or authorization;
- infer trust from lifecycle state;
- infer authorization from `ACTIVE` status;
- automatically replace registry descriptors;
- select a worker for execution;
- invoke capabilities;
- mutate policy;
- remove retired versions from historical records.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

The milestone becomes VERIFIED / COMPLETE only after the user's local focused and regression test receipt passes.
