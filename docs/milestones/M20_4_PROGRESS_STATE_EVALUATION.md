# M20.4 — Progress / State Evaluation

M20.4 compares recorded task state with explicitly supplied observations. It reports whether progress is unverified, aligned, or conflicted without mutating tasks or granting authority.

## Model

```text
Recorded Task State
        +
Explicit Observation / Evidence
        ↓
Progress Evaluation
```

`UNVERIFIED` means usable observation is absent or unknown. `ALIGNED` means the latest observation matches the recorded task state. `CONFLICTED` means the sources disagree; it does not declare either source false.

`ProgressEvidence` is immutable, provenance-bearing, and conflict-aware. `TaskProgressEvaluator` is read-only with respect to registered tasks and evaluates the latest observation deterministically.

## Authority boundary

```text
Progress ≠ Task State
Observation ≠ Task State
Conflict ≠ Falsehood
Unverified ≠ Failed
Evaluation ≠ Authorization
Evaluation ≠ Execution
Evaluation ≠ Next-Step Selection
```

M20.4 deliberately excludes readiness evaluation, scheduling, next-step selection, execution, authorization, worker assignment, automatic decomposition, and business-outcome truth evaluation.