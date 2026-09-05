# M23.11 — Current Context Freshness / Temporal Validity Contract

## Status
VERIFIED / COMPLETE

## Purpose
Establish a deterministic temporal-validity boundary for current-context evidence without treating context as timeless or authoritative.

## Contract
`EnvironmentCurrentContextFreshnessService` assesses one `EnvironmentCurrentContext` with an explicit observation timestamp, assessment timestamp, and maximum-age policy. It also assesses one `EnvironmentCurrentContextBundle` with one explicit observation timestamp per contained context.

Validity states are `CURRENT`, `STALE`, `FUTURE`, and explicit `INVALID` state. Only `CURRENT` evidence is temporally usable as current.

M23.9/M23.10 context artifacts do not contain temporal metadata, so M23.11 requires timestamps explicitly and never invents them.

## Authority boundary
Freshness is temporal evidence gating, not truth establishment. It does not establish truth, infer permissions/executability/capability availability, authorize execution, mutate upstream evidence or memory, retry providers, revoke anything, or establish adaptation truth.

## Files
- `src/core/environment_current_context_freshness.py`
- `src/core/tests/test_environment_current_context_freshness.py`
- `docs/decisions/055-current-context-freshness-temporal-validity-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification receipt
- Focused: `python -m unittest src.core.tests.test_environment_current_context_freshness -v` → **14/14 OK**
- Regression: `python -m unittest discover -s src\\core -p "test*.py"` → **631/631 OK**
- Combined: **645/645 OK**

No merge performed.
