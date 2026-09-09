# Decision 0203 — V2 SELF-scoped Runtime State

**Status:** IMPLEMENTED IN M27.11 / AWAITING LOCAL VERIFICATION

The changing JARVIS runtime state—Thinking, Learning, Working, Monitoring, Waiting, Needs You, model activity, delegation, communication, and resource pressure—is an internal observability concern and belongs primarily inside SELF.

Other interface spaces should expose only state that is functionally relevant to their job. Global navigation should not become a stream of internal runtime telemetry.

The sidebar has two presentation states: expanded navigation uses labels, while collapsed navigation uses icons only.

The visual language should favor readable typography, purposeful motion, quiet state beacons, and functional controls over decorative telemetry.

## Model orchestration principle

JARVIS may schedule model-backed work through a dedicated orchestration layer. The default strategy is sequential handoff: one model completes its assigned task before the next model receives the next task. Limited concurrency is an optimization only when actual system capacity and task boundaries make it safe.

System resource information is relevant to SELF and future orchestration decisions. When resource pressure rises, JARVIS should calm its workload by reducing concurrency, deferring non-urgent work, or waiting for capacity rather than blindly increasing activity.

These observations and scheduling decisions remain backend responsibilities. The UI only represents them.

## Invariants

- Internal runtime telemetry is primarily a SELF concern.
- Other spaces show only task-relevant state.
- Collapsed navigation uses icons only; expanded navigation uses labels.
- Visual state indicators communicate useful state without becoming noisy.
- Model orchestration is separate from presentation.
- Sequential model handoff is the default.
- Concurrency is conditional on actual system capacity and safe task separation.
- Resource pressure may influence scheduling, but the interface does not become orchestration authority.
