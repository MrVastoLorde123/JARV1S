# M10.4 — Memory Consolidation / Retrieval Improvement

## Status

**IMPLEMENTED — awaiting user verification**

M10.4 establishes the durable knowledge and retrieval boundary above M10.1 Experience, M10.2 Evaluation, and M10.3 Adaptation.

## Architecture

```text
Experience
   ↓
Evaluation
   ↓
Memory Candidate
   ↓
Explicit Consolidation
   ↓
Durable Memory View
   ↓
Deterministic Retrieval
```

## Implementation

`src/learning/consolidation.py` provides:

- `MemoryCandidate`
- `ConsolidatedMemory`
- `ConsolidationState`
- `MemoryConsolidator`
- `MemoryStore`
- `RetrievalResult`
- `MemoryRetriever`

The implementation is provider-neutral. It does not directly mutate the existing SQLite memory subsystem.

## Key behavior

Only directionally evaluated experiences can become memory candidates. Explicit acceptance is required before a candidate becomes accepted consolidated memory. Accepted memories can be reversed while preserving the previous candidate and provenance.

Retrieval considers accepted memories only and uses deterministic lexical overlap with bounded confidence weighting. The result is relevance evidence, not truth.

## Semantic walls

```text
Memory ≠ Truth
Memory ≠ Authority
Retrieval ≠ Permission
Consolidation ≠ Authorization
Relevance ≠ Certainty
History ≠ User Intent
Accepted Adaptation ≠ Universal Preference
```

## Non-goals

No policy mutation, authorization, execution, capability expansion, objective mutation, fabricated truth, model training, or autonomous self-modification.

## Verification target

```text
python -m unittest src.learning.tests.test_consolidation -v
python -m unittest
```
