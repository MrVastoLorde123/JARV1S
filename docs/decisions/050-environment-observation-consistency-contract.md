# M23.5 — Environment Observation Consistency Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide a deterministic boundary for comparing independent environment observations that refer to the same environment and domain without selecting an authoritative source.

## Contract
`EnvironmentObservationConsistencyService.compare(...)` compares exactly two `EnvironmentObservation` values with matching `environment_id` and `domain` and classifies their payloads as:

- `CONSISTENT` — canonical payload representations are equal.
- `CONFLICTING` — canonical payload representations differ.

`compare_many(...)` produces pairwise comparisons for observations sharing the same environment and domain while preserving input order. Observations from unrelated environments or domains are not compared by that batch method.

Mapping key order is normalized for deterministic comparison. The original observations are never mutated, merged, rewritten, discarded, retried, or selected as truth.

## Authority boundary
Consistency is evidence about agreement between observations, not truth.

This boundary does not:

- choose a winning adapter
- establish which observation is correct
- authorize execution
- grant permissions
- infer capability executability
- mutate memory
- rewrite observations
- retry failed observation providers
- revoke anything
- establish adaptation truth

A later policy/reasoning layer may use the explicit consistency result to decide whether additional observation, review, or action is appropriate.

## Architectural role
M23.3 intentionally rejects duplicate domains during direct snapshot composition. M23.5 introduces the separate evidence-comparison seam required before future aggregation can safely reason about multiple observers of the same domain.

Future shape:
`multiple observations → consistency/conflict assessment → policy/reasoning → optional aggregation`

Aggregation itself remains a later contract and must not silently collapse conflicting evidence.

## Files
- `src/core/environment_observation_consistency.py`
- `src/core/tests/test_environment_observation_consistency.py`
- `docs/decisions/050-environment-observation-consistency-contract.md`
