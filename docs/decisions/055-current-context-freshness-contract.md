# M23.11 — Current Context Freshness / Temporal Validity Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Define a deterministic temporal-validity boundary for current-context evidence without treating context as timeless or authoritative.

## Contract
`EnvironmentCurrentContextFreshnessService` assesses either:

- one `EnvironmentCurrentContext` using an explicit observation timestamp, assessment timestamp, and maximum age policy
- one `EnvironmentCurrentContextBundle` using one explicit observation timestamp per contained context

Freshness states are:

- `CURRENT` — observation age is within the configured maximum age
- `STALE` — observation age exceeds the configured maximum age
- `FUTURE` — observation timestamp is later than assessment time
- `INVALID` — reserved explicit state for invalid aggregate validity construction

The result preserves context/bundle identity, environment scope, observation timestamps, assessment time, age policy, freshness classification, per-context validity evidence where applicable, and recursively immutable lineage.

Because M23.9/M23.10 do not invent temporal metadata, M23.11 requires observation timestamps explicitly rather than inferring them from context structure.

## Authority boundary
Freshness answers whether supplied context evidence is temporally current under an explicit policy. It does not establish world truth.

It does not:

- establish truth
- invent timestamps
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- mutate context, observations, provenance, qualification, or memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.10 composes independent current-context evidence; M23.11 determines whether that evidence is temporally current enough for downstream world-model reasoning.

## Files
- `src/core/environment_current_context_freshness.py`
- `src/core/tests/test_environment_current_context_freshness.py`
- `docs/decisions/055-current-context-freshness-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_current_context_freshness -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
