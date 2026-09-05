# M22.5 — Plugin Isolation / Execution Sandbox Boundary

## Purpose

M22.5 establishes a bounded execution-isolation layer for plugins and capabilities. The first boundary is contract-level: define what containment a capability requests and whether the runtime can admit that containment. This milestone does not introduce host-process plugin execution yet.

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
Validation / Policy Decision
        ↓
Confirmation
        ↓
Authorization
        ↓
Sandbox Admission / Execution Isolation
        ↓
Execution
        ↓
Outcome / Feedback
```

## Core types

- `SandboxProfile` — immutable declarative containment/resource profile.
- `IsolationMode` — bounded isolation mode (`PROCESS`).
- `SandboxAdmissionEvaluator` — deterministic contract-admission evaluator; it does not authorize or execute.
- `SandboxAdmissionResult` — immutable admission result with explicit rejection reasons.
- `SandboxAdmissionStatus` — bounded `ADMISSIBLE` / `REJECTED` result state.
- `SandboxProfileRegistry` — explicit conflict-aware registry of profiles.
- `PluginIsolationError` — bounded isolation-contract error.

## Invariants

- Sandbox profiles are immutable metadata.
- Resource and containment constraints must be structurally valid.
- Read-only filesystems cannot simultaneously declare writable paths.
- CPU, memory, and timeout limits are positive and bounded where applicable.
- Sandbox admission is an infrastructure/containment check, not a permission or authorization check.
- An admissible result never implies permission, authorization, or execution.
- A rejected result carries deterministic rejection reasons.
- Sandbox profile registration is explicit and conflict-aware.
- Registry listing is deterministic.
- No sandbox operation launches a subprocess or plugin.

## Authority walls

```text
Sandbox ≠ Authorization
Isolation ≠ Trust
Admission ≠ Permission
Permission ≠ Execution
Process Boundary ≠ Authority Boundary
Containment ≠ Cancellation
Capability ≠ Worker
Plugin ≠ JARVIS
```

## Deliberate exclusions

M22.5 does not:

- spawn plugin subprocesses;
- execute arbitrary plugin code;
- convert sandbox admission into authorization;
- infer trust from successful isolation checks;
- grant permission;
- replace confirmation or authorization;
- revoke authorization;
- select workers;
- mutate policy;
- bypass the existing validation → policy → confirmation → authorization chain.

## Verification

M22.5 verification receipt: **10/10 focused + 9/9 M22.4 + 15/15 M22.3 + 9/9 M22.2 + 8/8 M22.1 + 487/487 core tests passed locally (538/538 total).**

Status: **VERIFIED / COMPLETE.**
