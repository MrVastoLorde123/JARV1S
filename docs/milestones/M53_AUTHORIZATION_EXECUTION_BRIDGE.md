# M53 — Authorization Execution Bridge

## Objective
Create the explicit bridge between the new M52 agency authorization boundary and the existing M7.10 provider-neutral execution preparation boundary.

## Contract
- bind only `GRANTED` M52 authorization
- require an existing `READY` M7.10 `ExecutionPreparation`
- require exact authorization identity match
- require exact confirmation identity match
- never create authorization
- never prepare execution
- never select providers or tools
- never execute capabilities

## Verification gate
```text
python -m unittest src.agency.tests.test_authorization_execution_bridge -v
python scripts/verify_m53_authorization_execution_bridge.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Draft/open by design; do not merge until the user supplies the local M53 receipt.
