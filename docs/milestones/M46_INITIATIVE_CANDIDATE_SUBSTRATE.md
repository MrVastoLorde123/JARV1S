# M46 — Initiative Candidate Substrate

## Purpose
Represent possible initiatives downstream of bounded reasoning without treating a candidate as truth, user intent, authorization, scheduling, or execution.

## Contract
- Candidates bind to one exact `ReasoningResult` identity.
- Supporting hypothesis IDs must exist in that reasoning result.
- Unresolved uncertainty is carried forward unchanged.
- Candidate output is descriptive/propositive only.
- No provider/model/tool selection, scheduling, authorization, or execution surface is introduced.

## Verification gate
```text
python -m unittest src.agency.tests.test_initiative_candidate -v
python scripts/verify_m46_initiative_candidate.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Draft/open by design; do not merge until the user supplies the local M46 receipt.
