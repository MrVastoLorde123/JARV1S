# M45 — Reasoning + Uncertainty Substrate

## Goal

Create a deterministic contract for downstream reasoning over the bounded M44 current context.

## Deliverables

- `src/agency/reasoning.py`
- `src/agency/tests/test_reasoning.py`
- `docs/decisions/M45.1-reasoning-uncertainty-substrate.md`
- `scripts/verify_m45_reasoning.py`
- public exports from `src.agency`

## Verification gate

```text
python -m unittest src.agency.tests.test_reasoning -v
python scripts/verify_m45_reasoning.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

## Acceptance boundary

A GREEN receipt requires all focused tests to pass, the repository-local contract check to pass, the UI production build to pass, and the full 3279-test core regression suite to remain green.

The PR remains draft/open/unmerged until the local receipt is supplied.
