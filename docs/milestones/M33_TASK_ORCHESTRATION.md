# M33 — Task Orchestration

## Purpose
Establish the bounded coordination layer that turns an M32 `WorkPlan` into deterministic work progression without crossing the existing authorization or execution boundaries.

## Scope
- immutable orchestration state
- per-step lifecycle state
- deterministic next-step selection
- dependency-aware progression using M32 readiness
- explicit active, blocked, failed, and terminal states
- public agency exports
- focused orchestration tests
- repository-local contract gate

## Boundary
M33 coordinates planned work. It does not authorize, invoke, execute, or verify actions. A selected step is a coordination result, not permission to act.

Consequential actions continue through the established authority/execution path and may use existing M8.5 controlled agency for already-authorized multi-step execution.

## Verification Gate
```text
python -m unittest src.agency.tests.test_task_orchestration -v
python scripts/verify_m33_task_orchestration.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

## Exit Criteria
M33 is complete when the focused orchestration suite is green, the contract gate passes, the UI build remains green, and the full core regression remains green.
