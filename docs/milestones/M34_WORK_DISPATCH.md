# M34 — Work Dispatch

## Goal

Establish the bounded bridge from an M33-selected plan step to an existing workforce assignment.

## Included

- immutable dispatch request/result contracts
- step-to-worker capability checking
- reuse of `WorkerRegistry` assignment validation
- explicit non-authorizing dispatch output
- focused dispatch tests
- repository-local verification gate
- decision documentation
- public agency exports

## Boundary

Dispatch does not authorize, invoke, execute, or verify consequential work. It only creates a bounded `WorkerAssignment` for downstream agency components. M7/M8 authority and M8.5 controlled agency remain authoritative for execution.

## Verification gate

```text
python -m unittest src.agency.tests.test_work_dispatch -v
python scripts/verify_m34_work_dispatch.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
