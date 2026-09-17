# M42 — World Model Substrate

## Purpose

Establish the first V7 World Model / Current Context boundary over existing world observations.

## Deliverables

- immutable `WorldModelFact`
- immutable `WorldModelSnapshot`
- explicit observation lineage on every modeled fact
- deterministic projection from existing `WorldObservation`
- bounded current-context queries by subject
- explicit non-truth/non-authority boundary
- focused world-model tests
- repository-local contract verification
- architecture decision documentation
- public agency exports

## Boundary

M42 models existing observations. It does not establish authoritative truth, infer user intent, authorize actions, execute capabilities, mutate memory, or select providers.

## Verification gate

```text
python -m unittest src.agency.tests.test_world_model -v
python scripts/verify_m42_world_model.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
