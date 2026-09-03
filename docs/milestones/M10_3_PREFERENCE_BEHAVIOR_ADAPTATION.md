# M10.3 — Preference / Behavior Adaptation

## Status

**IMPLEMENTED — awaiting user verification**

M10.3 establishes the bounded adaptation layer above M10.1 Experience and M10.2 Evaluation.

JARVIS can now represent a proposed change in preference or non-authoritative behavior, require explicit acceptance before recording the change, and reverse an accepted adaptation while preserving the previous value.

## Architecture

```text
Experience
   ↓
Evaluation
   ↓
Adaptation Proposal
   ↓
Explicit Acceptance
   ↓
Bounded Preference / Behavior State
   ↓
Reversal when required
```

## Implementation

`src/learning/adaptation.py` provides:

- `AdaptationKind`
- `AdaptationState`
- immutable `AdaptationProposal`
- immutable `AdaptationRecord`
- `AdaptationController`
- immutable conflict-aware `AdaptationStore`

`src/learning/tests/test_adaptation.py` provides focused contract coverage.

## Semantic walls

```text
Adaptation ≠ Authorization
Preference ≠ Policy
Behavior ≠ Authority
Feedback ≠ Truth
Evaluation ≠ User Intent
Learning Candidate ≠ Learned Policy
Adaptation ≠ Execution
Adaptation ≠ Self-Modification of Authority
```

## Key safety property

```text
JARVIS may change how it behaves
without changing what it is authorized to do.
```

Explicit user preferences are never silently overwritten. Accepted adaptations require an explicit acceptance reference, and reversal requires an explicit reversal reference.

## Non-goals

No policy mutation, authorization, execution, capability expansion, objective mutation, model training, irreversible self-modification, or hidden preference mutation.

## Verification target

```text
python -m unittest src.learning.tests.test_adaptation -v
python -m unittest
```
