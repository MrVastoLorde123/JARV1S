# M22.1 — Capability / Plugin Contract + Registry Boundary

## Purpose
M22.1 establishes the foundational contract and registry boundary for JARVIS's plugin/capability ecosystem.

The registry answers **what capability exists**. It does not answer **whether JARVIS is permitted to invoke it**.

## Contract

```text
Plugin / Capability Descriptor
          ↓
Registry Registration
          ↓
Deterministic Discovery
          ↓
Proposal / Worker Selection
          ↓
Validation / Policy
          ↓
Confirmation
          ↓
Authorization
          ↓
Execution
```

M22.1 stops at registration and discovery.

## Core types

- `CapabilityDescriptor` — immutable metadata for one capability.
- `CapabilityRegistry` — explicit, conflict-aware metadata registry.
- `PluginRegistryError` — bounded registry contract error.

## Invariants

- Capability descriptors require stable identity, name, version, and description.
- Descriptor metadata is declarative and contains no executable behavior.
- Descriptors are immutable.
- Registration is explicit and duplicate identities do not silently replace one another.
- Replacement requires an explicit `replace=True` request at the registry boundary.
- Discovery is deterministic by normalized capability identity.
- Lookup is normalization-stable for surrounding whitespace and case.
- Registry operations never invoke plugins, workers, schedulers, notifiers, or capabilities.
- Registration does not create trust, permission, authorization, or policy authority.
- Discovery returns metadata only.

## Authority walls

```text
Plugin ≠ JARVIS
Capability ≠ Permission
Registration ≠ Authorization
Discovery ≠ Execution
Manifest ≠ Trust
Availability ≠ Permission
Metadata ≠ Execution Request
```

## Deliberate exclusions

M22.1 does not:

- execute a plugin or capability;
- create an authorization decision;
- grant permissions;
- establish trust from registration alone;
- bypass validation, policy, confirmation, or authorization;
- schedule or notify;
- assign workers;
- mutate policy.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

The milestone becomes VERIFIED / COMPLETE only after the user's local focused and regression test receipt passes.
