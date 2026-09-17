# M48 — Information-Gain / Uncertainty-Reduction Substrate

M48 adds a bounded descriptive layer after initiative evaluation.

## Boundary

It represents opportunities to reduce explicitly unresolved uncertainty and records expected information gain. It does not establish truth, infer user intent, select a winner, schedule or notify, authorize actions, select providers/tools, execute capabilities, or mutate memory/world state.

## Inputs

- M47 `InitiativeEvaluationSet`
- its unresolved uncertainty set
- optional candidate lineage for each opportunity

## Outputs

- immutable `InformationGainOpportunity`
- immutable `InformationGainAssessment`
- preserved unresolved uncertainty

## Verification

```text
python -m unittest src.agency.tests.test_information_gain -v
python scripts/verify_m48_information_gain.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
