# M23.15 — World Model Change Assessment Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
M23.14 — World Model Uncertainty

## Purpose
Introduce a deterministic, immutable evidence boundary for identifying domain-level changes between two descriptive environment world models before any future belief revision or model mutation.

## Contract
`EnvironmentWorldModelChangeAssessmentService` compares exactly two `EnvironmentWorldModel` artifacts for the same environment.

It produces one `EnvironmentWorldModelChangeAssessment` that records:

- baseline and candidate model identities
- same-environment continuity
- changed and unchanged represented domains
- baseline and candidate missing-domain sets
- per-domain descriptive change details
- explicit lineage connecting the assessment to both source models

Domain order is deterministic: domains are considered in baseline represented-domain order followed by newly appearing candidate domains.

A domain is changed when its representation status changes or its descriptive state differs. A represented domain that remains equal is unchanged.

## Authority boundary
Change assessment is evidence only. It does not:

- establish world truth
- choose which model is authoritative
- revise or mutate either model
- select a winning state
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- mutate observations, provenance, memory, or context
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.13 introduced the descriptive world model. M23.14 introduced explicit uncertainty evidence. M23.15 introduces the change-detection seam required before later world-model revision/belief-state work.

This milestone intentionally does not decide whether a candidate change should replace baseline state. Belief revision, contradiction handling between competing models, historical state, persistence, and confidence calibration remain separate boundaries.

## Immutability
The assessment and nested change mappings are recursively immutable. Source models are never mutated.

## Files
- `src/core/environment_world_model_change_assessment.py`
- `src/core/tests/test_environment_world_model_change_assessment.py`
- `docs/decisions/056-world-model-change-assessment.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_change_assessment -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
