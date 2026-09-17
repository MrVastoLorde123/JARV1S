# M40 — Agency Lifecycle State

## Purpose

Provide one immutable observational aggregate for the existing V6 agency lifecycle without introducing a new authority or execution path.

## Deliverables

- immutable `AgencyLifecycleState`
- identity checks across WorkState, WorkPlan, and TaskOrchestration
- optional RecoveryReconciliation attachment
- explicit terminal and blocked read helpers
- explicit non-authority/non-execution context
- focused lifecycle-state tests
- repository-local verification gate
- architecture decision documentation
- public agency exports

## Boundary

M40 aggregates existing agency contracts for inspection. It does not authorize, execute, verify, invoke tools, select providers, manufacture evidence, or persist state.

## Verification gate

```text
python -m unittest src.agency.tests.test_lifecycle_state -v
python scripts/verify_m40_lifecycle_state.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
