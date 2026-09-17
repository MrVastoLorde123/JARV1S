# M52 — Authorization Decision Boundary

## Purpose

Create a deterministic authorization boundary downstream of explicit user confirmation.

## Included
- immutable `AuthorizationDecision`
- immutable `AuthorizationDecisionSet`
- explicit GRANTED / DENIED / BLOCKED dispositions
- exact confirmation-result identity enforcement
- authorization requires explicit CONFIRMED confirmation
- bounded constraints and rationale
- explicit authority/permission semantics only for GRANTED decisions
- no provider/tool selection
- no execution request or execution side effect
- focused tests and repository-local verifier

## Boundary

M52 may grant or deny authority for an already confirmed proposal. It does not select capabilities/providers/tools, request execution, perform execution, or establish truth or user intent.

## Verification gate

```text
python -m unittest src.agency.tests.test_authorization_decision -v
python scripts/verify_m52_authorization.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
