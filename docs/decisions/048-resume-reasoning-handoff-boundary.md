# Decision 048 — Resume-to-Reasoning Handoff Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a host-neutral handoff that combines the explicit M65 resume transition with exactly one M64 reasoning/tool-feedback pulse.

The handoff:

- requires an explicit resume request for persisted waiting/paused jobs;
- carries confirmation only as an ephemeral signal into the next bounded pulse;
- never persists confirmation as authorization state;
- injects explicit input context before the next reasoning cycle;
- executes at most one M64 pulse after resumption;
- returns the resulting persisted job and pulse evidence.

## Safety boundary

The handoff does not replace the M61 tool gate. Explicit confirmation authorizes the next gate evaluation only; provider output remains advisory and persistence remains state storage rather than permission.
