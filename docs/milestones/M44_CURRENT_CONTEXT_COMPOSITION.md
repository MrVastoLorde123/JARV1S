# M44 — Current Context Composition

## Purpose

Provide one immutable bounded current-context object for downstream reasoning from already-qualified M43 world-model facts.

## Deliverables

- immutable `CurrentContextFact`
- immutable `CurrentContext`
- deterministic admission of `USABLE` facts only
- explicit exclusion of stale, invalid, and conflicting facts
- snapshot/qualification identity checks
- non-truth/non-authority boundary
- focused current-context tests
- repository-local contract verification
- architecture decision documentation
- public agency export

## Boundary

M44 composes qualified world-model facts. It does not establish truth, infer user intent, authorize actions, execute capabilities, mutate memory, or select providers.

## Verification gate

```text
python -m unittest src.agency.tests.test_current_context -v
python scripts/verify_m44_current_context.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
