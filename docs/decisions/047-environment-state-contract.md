# M23.2 — Environment State Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish a provider-neutral, immutable representation of the environment known to JARVIS so later model routing, capability selection, anomaly detection, scheduling, and optimization can reason from current system state without embedding hardware assumptions into individual services.

## Contract
`EnvironmentSnapshot` records descriptive state across:

- hardware
- software
- network
- installed/available models
- capabilities
- permissions
- performance observations
- costs
- resources
- metadata

`EnvironmentSnapshotService` constructs validated snapshots from observed inputs.

All domain mappings are recursively frozen so the snapshot remains an immutable evidence/state artifact.

## Authority boundary
Environment state is descriptive, not authoritative.

It does not:

- grant authorization
- grant capability permission
- request execution
- execute tools
- establish adaptation truth
- infer that a capability is executable merely because it is present

Permissions are recorded as observed state; they are not created or elevated by the snapshot.

## Architectural role
M23.2 prepares the substrate for future environment-aware decisions such as:

`environment state → model/capability assessment → routing or planning`

The actual routing/selection policy remains a separate concern.

This boundary deliberately does not probe the host directly, because hardware discovery, operating-system inspection, telemetry collection, and external-service health checks are observation adapters that should remain replaceable and composable.

## Files
- `src/core/environment_model.py`
- `src/core/tests/test_environment_model.py`
- `docs/decisions/047-environment-state-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_model -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
