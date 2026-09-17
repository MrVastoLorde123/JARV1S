# M49 — Proactive Proposal Substrate

## Purpose
Represent bounded proactive proposals downstream of initiative evaluation and information-gain assessment.

## Included
- immutable `ProactiveProposal`
- immutable `ProactiveProposalSet`
- exact evaluation-set identity enforcement
- information-gain opportunity lineage validation
- candidate lineage validation
- unresolved uncertainty lineage preservation
- explicit non-truth/non-intent/non-authority/non-scheduling/non-notification/non-authorization/non-execution semantics
- focused tests and repository-local verifier

## Verification gate
```text
python -m unittest src.agency.tests.test_proactive_proposal -v
python scripts/verify_m49_proactive_proposal.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

## Boundary
M49 proposes possible user-facing initiatives; it does not decide that a proposal reflects user intent, schedule it, notify the user, authorize it, or execute it.
