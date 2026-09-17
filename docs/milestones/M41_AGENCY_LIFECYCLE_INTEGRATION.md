# M41 — Agency Lifecycle Integration

## Purpose

Provide one immutable integration read model spanning the existing V6 agency lifecycle from work planning through execution observation, independent verification, recovery, and operational reconciliation.

## Deliverables

- immutable `AgencyLifecycleIntegration`
- cross-stage execution and work identity validation
- execution outcome and verification linkage
- optional recovery decision and reconciliation linkage
- explicit lifecycle terminal/blocked helpers
- explicit non-authority/non-execution context
- focused integration tests
- repository-local verification gate
- architecture decision documentation
- public agency exports

## Boundary

M41 integrates existing contracts for inspection. It does not authorize, execute, verify, invoke tools, select providers, manufacture evidence, or persist state.

## Verification gate

```text
python -m unittest src.agency.tests.test_lifecycle_integration -v
python scripts/verify_m41_lifecycle_integration.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
