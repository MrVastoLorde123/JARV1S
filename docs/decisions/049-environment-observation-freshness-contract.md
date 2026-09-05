# M23.4 — Environment Observation Freshness/Validity Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide deterministic temporal validity semantics for environment observations without mutating the source observation or silently treating stale state as current state.

## Contract
`EnvironmentObservationFreshnessService` assesses one immutable `EnvironmentObservation` against:

- the observation timestamp
- the assessment timestamp
- a maximum permitted age

The resulting immutable `EnvironmentObservationValidity` preserves the observation identity, environment identity, domain, timestamps, configured age bound, computed age, and a deterministic `ObservationFreshness` classification.

Classifications:

- `CURRENT` — age is non-negative and within the configured maximum age; safe to treat as current by this contract.
- `STALE` — age exceeds the configured maximum age; not usable as current.
- `FUTURE` — observation timestamp is later than the assessment timestamp; not usable as current.

Timestamps must be timezone-aware and are normalized to UTC. Maximum age must be non-negative numeric input.

`assess_many` preserves input order and rejects duplicate observation identities rather than merging them implicitly.

## Authority boundary
Freshness is an assessment signal, not authority. It does not authorize execution, grant permission, imply capability executability, mutate memory, rewrite observations, establish truth, or trigger retries/revocation.

A stale observation remains valid historical evidence; this boundary only prevents the derived assessment from being interpreted as current state.

## Architectural relationship
`M23.4` sits after `M23.3` observation acquisition and before future environment-aware routing/planning/anomaly decisions:

`Observation → Freshness/Validity Assessment → Environment-Aware Decision`

The raw `EnvironmentObservation` remains provider-neutral and immutable. Timestamp acquisition remains the responsibility of the observation adapter/caller; the freshness service deliberately does not probe clocks, hosts, or external systems itself.

## Files
- `src/core/environment_observation_freshness.py`
- `src/core/tests/test_environment_observation_freshness.py`
- `docs/decisions/049-environment-observation-freshness-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_observation_freshness -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
