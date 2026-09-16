# M36 — Agency Execution Bridge

## Scope

Connect the verified M35 `ExecutionHandoff` to the existing M8.5 `ControlledAgency` runtime.

## M36.1 — Bridge contract

`run_execution_handoff()` accepts only an existing `ControlledAgency`, `ExecutionHandoff`, and `WorkingContext` and feeds the handoff's exact READY preparation into the existing agency runtime.

## M36.2 — Result linkage

`AgencyExecutionBridgeResult` preserves execution identity, worker assignment identity, bounded agency observations, stop reason, and success state.

## M36.3 — Authority separation

No authorization creation, policy evaluation, execution preparation, provider selection, or direct invocation is introduced.

## M36.4 — Verification gate

```text
python -m unittest src.agency.tests.test_execution_bridge -v
python scripts/verify_m36_execution_bridge.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

## Boundary

M36 is an execution handoff bridge, not a second execution engine. Existing M7/M8 authority and M8.5 controlled agency remain authoritative.
