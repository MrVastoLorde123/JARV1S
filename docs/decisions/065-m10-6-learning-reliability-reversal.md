# Decision 065 — M10.6 Learning Reliability / Reversal

## Status

IMPLEMENTATION IN PROGRESS

## Decision

M10.6 introduces a provider-neutral reliability lifecycle for learned artifacts. New evidence may reduce confidence in an existing learning artifact without deleting its historical record. Reliability state is explicit, immutable, conflict-aware, and reversible where permitted.

## Boundary

```text
Learned Artifact
      ↓
New Evidence / Observation
      ↓
Reliability Assessment
      ↓
RETAINED / WATCH / CONFLICTED / SUSPENDED / REVERSED / SUPERSEDED
      ↓
Explicit Learning / Memory Boundary
      ↓
Future Retrieval / Reasoning Context
```

## Reliability model

`ReliabilityEvidence` contains an explicit reliability signal:

- `True` supports continued reliability
- `False` weakens reliability
- `None` is directionless and causes a `WATCH` state

Conflicting positive and negative evidence produces `CONFLICTED` rather than silently selecting one side.

## Lifecycle

Initial assessments may produce `RETAINED`, `WATCH`, `SUSPENDED`, or `CONFLICTED`.

Explicit transitions preserve history through predecessor references. Terminal states require explicit references:

- `REVERSED` means the learned artifact should no longer be treated as active learning.
- `SUPERSEDED` means a replacement learning artifact exists and the replacement relationship is explicit.

Neither state deletes the original history.

## Semantic walls

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

## Non-goals

M10.6 does not grant authority, authorize actions, execute plugins, expand capabilities, mutate policy, or silently overwrite explicit user memory. A newer observation is evidence, not automatic authority.

## Relationship to prior milestones

- M10.1 supplies immutable experience lineage.
- M10.2 supplies explicit outcome evaluation.
- M10.3 supplies explicit accepted/rejected/reversed behavior adaptation.
- M10.4 supplies accepted durable-memory artifacts and deterministic retrieval.
- M10.5 supplies reasoning-quality feedback.

M10.6 governs whether learned artifacts remain reliable enough to participate in future learning or reasoning. It does not replace or bypass the explicit boundaries above.
