# M32 — Work Planning

**Status:** implementation in progress.

M32 turns the verified Work State substrate into a deterministic, bounded planning layer. Plans describe proposed work; they do not authorize or execute it.

## Milestone chain

- **M32.1 — Planning contract:** define immutable plans and steps.
- **M32.2 — Role-aware steps:** carry the dynamic operational role into each step.
- **M32.3 — Dependencies:** represent bounded step dependencies and deterministic readiness.
- **M32.4 — Authority separation:** planning exposes no authorization or execution surface.
- **M32.5 — Verification gate:** focused planning tests, repository-local validation, UI build, and the established core regression baseline.

## Boundary

M32 is planning and orchestration context. It does not select policy, grant authority, invoke tools, or verify outcomes.

## Verification

```text
python -m unittest src.agency.tests.test_work_planning -v
python scripts/verify_m32_work_planning.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

M32 closes only after the user-local receipt is green.
