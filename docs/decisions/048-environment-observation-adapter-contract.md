# M23.3 — Environment Observation Adapter Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Define a provider-neutral, replaceable boundary between environment observation and the immutable environment state model introduced by M23.2.

Observation sources may later include operating-system probes, hardware discovery, telemetry collectors, model-server checks, network health checks, or external-service adapters. Those providers remain outside JARVIS's environment-state core.

## Contract
`EnvironmentObservationAdapter` exposes:

- `adapter_id`
- `domain`
- `observe(environment_id)` → exactly one `EnvironmentObservation`

`EnvironmentObservation` records:

- observation identity
- adapter identity
- environment identity
- one explicit environment domain
- descriptive payload
- descriptive metadata

Supported domains are the M23.2 environment domains:

`hardware`, `software`, `network`, `models`, `capabilities`, `permissions`, `performance`, `costs`, `resources`, `metadata`.

Observation payloads and metadata are recursively immutable.

## Composition
`EnvironmentObservationService`:

1. validates environment identity;
2. rejects duplicate adapter identities;
3. rejects duplicate domains rather than silently merging conflicting observations;
4. invokes each adapter exactly once;
5. requires the exact `EnvironmentObservation` type;
6. verifies adapter identity, domain, and environment identity;
7. wraps adapter failures as `EnvironmentObservationError`;
8. composes the collected observations into `EnvironmentSnapshot` through `EnvironmentSnapshotService`;
9. records observation source identity as descriptive snapshot metadata.

Missing domains remain empty and do not imply that the domain is unavailable or unsupported.

## Authority boundary
Observation is evidence, not authority.

This boundary does not:

- grant authorization
- elevate permissions
- imply capability executability
- request execution
- execute tools
- retry failed observations automatically
- mutate memory
- establish adaptation truth

A recorded `permissions` observation is only a report of observed state. A recorded `capabilities` observation is not a permission grant.

## Architectural relationship
`M23.2 Environment State → M23.3 Observation Adapters → later environment-aware reasoning/routing/planning`

M23.3 does not implement hardware probing itself. Providers remain replaceable and independently testable.

## Files
- `src/core/environment_observation.py`
- `src/core/tests/test_environment_observation.py`
- `docs/decisions/048-environment-observation-adapter-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_observation -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
