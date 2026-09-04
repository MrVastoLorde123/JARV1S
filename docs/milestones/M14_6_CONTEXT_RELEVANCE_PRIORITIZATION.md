# M14.6 — Context Relevance / Prioritization

## Purpose

Provide a deterministic boundary for ranking already-known context by an explicit relevance judgment.

## Contract

`ContextRelevance` attaches a bounded score and reasons to a `DomainReference`.
`ContextRelevanceRanking` validates deterministic ordering and provides bounded views.
`rank_relevance` performs ordering only; it does not create or infer the judgments.

## Boundaries

- Relevance ≠ Truth
- Relevance ≠ Fact
- Relevance ≠ User Intent
- Relevance ≠ Importance
- Relevance ≠ Authorization
- Relevance ≠ Policy
- Prioritization ≠ Instruction
- Prioritization ≠ Permission
- Ranking ≠ Execution

## Non-goals

This slice does not infer relevance from language, infer user intent, mutate context, authorize actions, execute work, or establish causal truth.

## Verification

Focused tests live in `src/context/tests/test_relevance.py`.
