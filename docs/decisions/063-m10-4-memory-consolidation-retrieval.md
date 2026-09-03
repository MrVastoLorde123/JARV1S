# Decision 063 — M10.4 Memory Consolidation / Retrieval Improvement

## Status

**ACCEPTED**

M10.4 establishes a durable knowledge boundary above the verified M10.1 Experience, M10.2 Evaluation, and M10.3 Adaptation boundaries.

## Decision

Evaluated experience may produce an explicit `MemoryCandidate`. The candidate is not durable memory until explicitly accepted. Accepted consolidated memory retains provenance and may be explicitly reversed.

Retrieval operates only over accepted consolidated memories and returns inspectable relevance results. Relevance is a retrieval signal, not truth or certainty.

The existing mutable SQLite memory subsystem is not directly mutated by M10.4. This stage establishes the provider-neutral contract that a future integration may consume safely.

## Contract

```text
Experience
    ↓
Evaluation
    ↓
MemoryCandidate
    ↓
Explicit Consolidation
    ↓
ConsolidatedMemory
    ↓
Deterministic Retrieval
    ↓
RetrievalResult
```

## States

```text
PROPOSED
ACCEPTED
REJECTED
REVERSED
```

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

## Required properties

- Only directionally evaluated experiences may be consolidated.
- Evaluation identity must match the experience being consolidated.
- Accepted adaptations may contribute provenance, but rejected/reversed adaptations may not.
- Consolidation requires explicit acceptance provenance.
- Reversal requires explicit reversal provenance and preserves the previous candidate.
- Duplicate memory identities are explicit conflicts.
- Retrieval considers accepted memories only.
- Retrieval ranking is deterministic and inspectable.
- Memory and retrieval serialization explicitly deny truth, authority, authorization, and execution semantics.
- M10.4 does not mutate M7 authority, M8 execution, M9 workforce, objectives, capabilities, or policy.

## Non-goals

M10.4 does not implement truth inference, automatic policy mutation, authorization, execution, capability expansion, objective mutation, model training, or autonomous self-modification.
