# CS9 — Architecture Cleanup

## Boundary

CS9 removes obsolete compatibility scaffolding that became unnecessary after the canonical runtime and authority paths were established.

This stage is not a feature expansion. The objective is to leave one understandable architecture instead of retaining historical alternate contracts.

## Cleanup performed

### Coding execution observation bridge

Removed the `ObservingToolInvoker.__eq__` compatibility override that existed solely to preserve identity semantics for legacy dependency-injection contracts.

The wrapper remains an observational adapter. It does not impersonate its delegate.

### Execution observation contract

Removed the optional-state compatibility fallback from `ExecutionObservation`.

The canonical contract now requires:

```python
ExecutionObservation(
    plan=plan,
    execution=execution,
    state=state,
)
```

State is derived by the guarded execution loop before the observation is constructed. The observation no longer silently reconstructs missing state from an older calling convention.

## Why these are cleanup rather than behavior changes

Both removed paths existed to preserve historical construction/injection behavior. The current canonical runtime already supplies the explicit state and explicit wrapper dependencies.

Keeping those shims would preserve alternate contracts after the architecture had converged.

No authority boundary was moved:

- policy remains the authority gate;
- confirmation remains explicit;
- authorization evidence remains durable and fail-closed;
- sandbox admission remains deterministic;
- execution remains downstream of the canonical gate;
- observations remain observational;
- learning remains non-authoritative.

## Verification

The dedicated CS9 workflow verifies:

1. retired compatibility signatures are absent;
2. historical interface/tool/AI closure gates pass;
3. authoritative core regression passes;
4. UI lockfile installation and production build pass.

The CS8 baseline remains the comparison point:

- CS8 core regression: 3304/3304
- CS8 focused red-team: 10/10 core + 1/1 model boundary

## Acceptance criteria

CS9 is VERIFIED / CLOSED only when:

1. obsolete compatibility paths are removed;
2. no replacement execution or authority path is introduced;
3. the authoritative core regression passes on the cleanup head;
4. historical interface/AI gates pass;
5. UI reproducibility remains green;
6. the canonical contracts are explicit rather than silently accepting legacy forms;
7. no `main` change or merge is performed.

