# M10.7 — Intelligence Integration

**Status: IN PROGRESS**

## Goal

Integrate bounded M10 learning outputs into a single immutable reasoning-context boundary without turning learned information into truth, authority, permission, or unrestricted agency.

## Verified design

- `IntelligenceContext` is immutable and provider-neutral.
- Retrieval results enter only as relevance evidence.
- `REVERSED` and `SUPERSEDED` learning is excluded from active reasoning context.
- Only explicitly `ACCEPTED` adaptations influence active behavioral context.
- Evaluations, quality feedback, and reliability remain typed and attributable.
- Serialization explicitly denies truth, authority, authorization, execution, and policy mutation.

## Core invariants

```text
Intelligence Context ≠ Truth
Intelligence Context ≠ Authority
Learning ≠ Permission
Relevance ≠ Certainty
Adaptation ≠ Authorization
Evaluation ≠ Intent
Reliability ≠ Truth
Integration ≠ Execution
Intelligence ≠ Unbounded Agency
```

## Flow

```text
Experience
   ↓
Evaluation
   ↓
Adaptation / Memory / Quality / Reliability
   ↓
Intelligence Integration
   ↓
IntelligenceContext
   ↓
Future Reasoning
   ↓
M7 Authority
```

## Verification target

Focused M10.7 tests must cover context immutability, bounded filtering, reliability exclusion, accepted-adaptation filtering, provenance, deterministic serialization, and explicit denial of authority/execution semantics.
