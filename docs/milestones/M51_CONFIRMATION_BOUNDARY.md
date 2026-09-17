# M51 — Confirmation Boundary

## Purpose
Establish a bounded confirmation layer between scheduling/notification proposals and downstream authorization.

## Contract
- Confirmation is explicit user response data, not inferred intent.
- CONFIRMED does not grant authority or permission.
- DECLINED and EXPIRED remain terminal response states for that request.
- Pending requests cannot carry a claimed response.
- Every request is bound to an exact M50 scheduling/notification proposal set and proposal identity.

## Non-goals
M51 does not authorize actions, select providers or tools, schedule, notify, execute capabilities, mutate memory, or establish truth.

## Verification gate
```text
python -m unittest src.agency.tests.test_confirmation -v
python scripts/verify_m51_confirmation.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Draft/open by design until the user supplies the local M51 receipt.
