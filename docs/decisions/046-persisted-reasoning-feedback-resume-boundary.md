# Decision 046 — Persisted Reasoning Feedback Resume Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a host-neutral reasoning execution pulse that resumes an autonomous job from persisted state, runs one reasoning/tool-feedback cycle, records the resulting observation/context as the next immutable job step, and persists the changed snapshot before returning.

The pulse:

- restores the exact persisted `AutonomousJob` identity;
- starts queued work before the first reasoning cycle;
- executes at most one bounded reasoning/tool-feedback cycle per pulse;
- persists successful progress through the existing `AutonomousJobPersistenceService`;
- preserves waiting-for-authorization/tool/input states so a later pulse can resume them;
- does not select providers, bypass confirmation, mutate authorization, or own tool execution.

## Resume semantics

A successful tool-feedback cycle remains `RUNNING` so the next pulse can reason over the newly persisted tool evidence. A confirmation or other wait becomes the corresponding persisted waiting state.

## Safety boundary

Persistence is state storage, not permission. A resumed job does not imply authorization. Provider output remains advisory and tool execution remains behind the existing M61 gate.
