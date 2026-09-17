# M47 — Initiative Evaluation Substrate

## Purpose
Represent descriptive evaluations of initiative candidates without collapsing evaluation into prioritization, scheduling, authorization, or execution.

## Boundary
M47 consumes the M46 initiative-candidate set and produces immutable evaluation records tied to the exact candidate-set identity.

It does not:
- establish truth;
- infer user intent as fact;
- choose or rank a winner;
- schedule or notify;
- authorize actions;
- select providers, tools, or capabilities;
- execute work;
- mutate memory or world state.

## Verification gate
```text
python -m unittest src.agency.tests.test_initiative_evaluation -v
python scripts/verify_m47_initiative_evaluation.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
