# M23.8 — Environment Observation Evidence Qualification Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide one immutable, deterministic qualification artifact that gates environment observation evidence before downstream world-model/current-context reasoning.

## Contract
`EnvironmentObservationEvidenceQualificationService` qualifies either:

- one `EnvironmentObservation` using one matching `EnvironmentObservationValidity` and `EnvironmentObservationProvenance`
- one `EnvironmentObservationAggregate` using aligned validities, complete matching consistency evidence, and matching provenance

Qualification states are:

- `USABLE` — required evidence gates pass
- `UNUSABLE` — supplied evidence is structurally valid but temporal validity is not current
- `CONFLICTING` — supplied pairwise consistency evidence contains a conflict
- `INSUFFICIENT` — required evidence is structurally aligned but incomplete for qualification

The result preserves source observation IDs, adapter IDs, temporal classifications, consistency classifications, provenance identity, qualification time, reasons, and recursively immutable lineage metadata.

Identity and scope mismatches are contract violations and are rejected rather than silently classified.

## Authority boundary
Qualification answers whether the supplied evidence bundle satisfies deterministic evidence gates for downstream reasoning. It does not establish whether the underlying world is true.

It does not:

- select an authoritative source
- establish truth
- authorize execution
- grant permissions
- imply capability executability or availability
- mutate observations, aggregates, provenance, or memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.3 established replaceable observation adapters; M23.4 established temporal validity; M23.5 established consistency/conflict evidence; M23.6 established safe aggregation; M23.7 established explicit source provenance. M23.8 creates the evidence-gating seam between these observation artifacts and later world-model/current-context construction.

The output is downstream-reasoning evidence, not authoritative world state.

## Files
- `src/core/environment_observation_evidence_qualification.py`
- `src/core/tests/test_environment_observation_evidence_qualification.py`
- `docs/decisions/053-environment-observation-evidence-qualification-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_observation_evidence_qualification -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
