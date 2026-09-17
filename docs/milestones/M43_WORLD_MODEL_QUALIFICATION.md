# M43 — World Model Qualification

## Purpose

Qualify existing M42 world-model facts for freshness and same-subject/domain conflicts before downstream reasoning consumes them.

## Deliverables

- immutable `WorldFactAssessment`
- immutable `WorldModelQualification`
- deterministic freshness classification
- explicit conflict preservation with peer fact identities
- fail-closed invalid/future timestamp handling
- no truth arbitration
- focused qualification tests
- repository-local contract verification
- architecture decision documentation

## Boundary

M43 evaluates current-context usability. It does not establish authoritative truth, infer user intent, authorize actions, execute capabilities, mutate memory, or select providers.

## Verification gate

```text
python -m unittest src.agency.tests.test_world_model_qualification -v
python scripts/verify_m43_world_model.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
