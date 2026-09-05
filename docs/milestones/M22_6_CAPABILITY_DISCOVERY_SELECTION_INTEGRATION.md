# M22.6 — Capability Discovery + Selection Integration

## Purpose

M22.6 makes the existing provider-neutral capability discovery and selection path an explicit integration boundary.

The integration composes the existing:

```text
ToolCapabilityGateway
        ↓
CapabilityCatalog
        ↓
CapabilitySelectionService
        ↓
CapabilitySelector
        ↓
CapabilityDiscoverySelection
```

The result is an inspectable snapshot of what was discovered and what the selector proposed for an intent.

## Contract

- `CapabilityCatalog` remains a read-only view over the existing capability gateway.
- `CapabilitySelector` remains provider-neutral and replaceable.
- `CapabilitySelectionService` performs discovery and selection only.
- `CapabilityDiscoverySelection` captures the discovery snapshot and ranked selection together so downstream components can inspect exactly what was selected from.
- Selection results reference capabilities from the same discovery snapshot; selection cannot silently introduce an undiscovered capability.
- The integration never creates a `ToolRequest`, invokes a tool, grants permission, creates authorization, performs sandbox admission, or mutates policy.

## Invariants

- Discovery is deterministic and read-only.
- Selection is deterministic for the deterministic selector.
- Discovered capability definitions are immutable values from the existing tool boundary.
- Provider-backed selectors may replace the deterministic selector without changing the execution boundary.
- The integrated snapshot is immutable.
- Snapshot query and selection query must match.
- Every selected candidate must originate from the snapshot's discovered capability values.
- Discovery and selection do not imply permission, authorization, confirmation, sandbox admission, or execution.
- The existing `PolicyGate` remains the invocation boundary.

## Authority walls

```text
Discovery ≠ Permission
Selection ≠ Authorization
Selection ≠ Execution
Capability ≠ Permission
Capability ≠ Worker
Proposal ≠ Authorization
Sandbox ≠ Authorization
Policy ≠ Authorization
```

## Deliberate exclusions

M22.6 does not:

- invoke tools or plugins;
- construct privileged execution requests;
- authorize selected capabilities;
- interpret selection as user confirmation;
- bypass `PolicyGate`;
- assign workers;
- infer trust, permission, or authorization from selection rank;
- mutate capability registries or policy during discovery/selection;
- perform sandbox admission or process isolation.

## Relationship to the existing execution path

```text
Capability Discovery / Selection
              ↓
       Structured Proposal
              ↓
     Argument / Request Build
              ↓
       Validation / Policy
              ↓
          Confirmation
              ↓
         Authorization
              ↓
           Sandbox
              ↓
          Execution
```

M22.6 stops at the structured discovery/selection proposal. Later layers remain responsible for validation, policy, confirmation, authorization, sandbox admission, and execution.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.6 becomes VERIFIED / COMPLETE only after the user's local focused and regression receipt passes.
