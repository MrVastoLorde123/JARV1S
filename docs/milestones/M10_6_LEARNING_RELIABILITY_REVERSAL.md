# M10.6 — Learning Reliability / Reversal

**Status: IMPLEMENTED — awaiting user verification**

## Goal

Make learned knowledge safe to distrust, suspend, supersede, or reverse when later evidence weakens or contradicts it, while preserving lineage and auditability.

## Implementation

`src/learning/reliability.py` provides:

- `ReliabilityState`
- immutable `ReliabilityEvidence`
- immutable `ReliabilityAssessment`
- immutable `ReliabilityRecord`
- `LearningReliabilityController`
- immutable conflict-aware `ReliabilityStore`

## Reliability states

```text
RETAINED
WATCH
CONFLICTED
SUSPENDED
REVERSED
SUPERSEDED
```

`WATCH` is used when available evidence is directionless. `CONFLICTED` is used when explicit evidence supports and weakens reliability at the same time. `SUSPENDED` is used when evidence weakens reliability. `REVERSED` and `SUPERSEDED` are explicit terminal lifecycle states.

## History rule

Reliability changes append new immutable records linked to their predecessor. Reversal and supersession therefore change current eligibility without erasing the historical artifact or its prior state.

## Core invariants

```text
Learning ≠ Truth
Reversal ≠ Deletion
Reliability ≠ Certainty
Conflict ≠ Permission
Supersession ≠ Authority
Retraction ≠ Execution
New Evidence ≠ Automatic Policy Change
Learning Reliability ≠ Authorization
History ≠ Current Truth
Memory Status ≠ User Intent
```

## Verification target

Focused tests:

```bash
python -m unittest src.learning.tests.test_reliability -v
```

Learning-area discovery:

```bash
python -m unittest discover -s src.learning.tests -p "test*.py"
```

The repository-wide discovery baseline entering M10.6 is **997/997**. Cumulative milestone-specific executions are tracked separately.
