# Operational JARVIS

## Purpose

This document defines the operationalization program that turns the verified JARVIS architecture into one runnable, continuously improvable machine.

The objective is not to replace the existing architecture. The objective is to compose it.

## Strategic rule

JARVIS must become alive, runnable, and useful before the project continues expanding the platform as an isolated collection of subsystems.

Once JARVIS is operational, new subsystems may be added freely when they create real value. The living system becomes the primary source of operational evidence:

```
USE JARVIS
    ↓
discover weakness
    ↓
improve JARVIS
    ↓
USE JARVIS BETTER
    ↓
discover next weakness
    ↓
improve again
```

Building without a runnable JARVIS is therefore a strategic loss: engineering decisions are made against isolated contracts instead of a living system that can expose its real weaknesses.

## Canonical operational loop

The operational system must support one causal lifecycle:

```
USER
  ↓
UNDERSTAND
  ↓
REMEMBER / CONTEXTUALIZE
  ↓
OBSERVE CURRENT STATE
  ↓
REASON
  ↓
FORM GOAL
  ↓
PLAN
  ↓
PROPOSE
  ↓
CAPABILITY DISCOVERY / SELECTION
  ↓
VALIDATION
  ↓
POLICY
  ↓
CONFIRMATION (when required)
  ↓
AUTHORIZATION
  ↓
EXECUTION
  ↓
OBSERVATION
  ↓
VERIFICATION
  ↓
RECOVERY / CONTINUATION (when permitted)
  ↓
REPORT RESULT
  ↓
EXPERIENCE / OUTCOME
  ↓
LEARNING
  ↓
FUTURE BEHAVIOR
```

## Operational state

Every real operation must preserve causal identity and expose its current lifecycle state. The canonical state vocabulary is:

- REQUESTED
- UNDERSTANDING
- CONTEXTUALIZED
- PLANNED
- PROPOSED
- AWAITING_CONFIRMATION
- AUTHORIZED
- EXECUTING
- OBSERVING
- VERIFYING
- RECOVERING
- WAITING
- COMPLETED
- FAILED
- CANCELLED

These states describe runtime state. They do not grant authority.

## Authority invariants

The operational composition must preserve the existing authority walls:

```
Intelligence ≠ Authority
Learning ≠ Authority
Planning ≠ Execution
Proposal ≠ Authorization
Capability ≠ Permission
Authorization ≠ Verification
Execution Result ≠ Verified Effect
Memory ≠ User Intent
Observation ≠ Truth
Confidence ≠ Certainty
```

No operational integration may create a second authority path.

## Program boundaries

### OPS-00 — Operational Contract

Establish the canonical lifecycle, causal identity, completion semantics, waiting semantics, failure semantics, and acceptance vocabulary for one real operation.

### OPS-01 — One Runtime Spine

Collapse the competing runtime centers into one canonical operational composition root.

The end-user path must resolve to one runtime identity regardless of whether a capability originated in an earlier milestone or a newer subsystem.

### OPS-02 — Understanding → Action

Wire natural-language intent classification into the actual local runtime so ordinary user language can correctly enter conversation, question, task, or tool paths.

### OPS-03 — Cognition → Plan → Proposal

Make the existing cognitive runtime materially feed the operational path rather than existing only as inspectable advisory metadata.

Cognition remains advisory and non-authoritative.

### OPS-03 live implementation

The live `JARVIS` task path now runs the canonical cognitive runtime inside the existing task execution boundary and carries its goal/plan/proposal lineage onto the deterministic execution plan.

The current causal seam is:

```
intent
  ↓
capability discovery / realization (existing bounded path)
  ↓
deterministic execution plan
  ↓
cognitive context attached to the operational plan
  ├─ world snapshot
  ├─ reasoning result
  ├─ goal
  ├─ selected advisory plan
  └─ proposal
        ↓
validation / policy / confirmation / authorization / execution
```

Cognition changes the inspectable plan context, but it does not become an execution authority. Existing task and planner object contracts remain unchanged.

A cognitive-runtime failure is represented as `UNAVAILABLE`; it does not silently become permission to act and it does not create a second execution path.

The compatibility `UnifiedRequestRuntime` avoids running cognition twice when it wraps an already-integrated JARVIS processor.
### OPS-04 — Capability → Agency

Connect goal/planning outputs to real capability discovery, selection, realization, validation, policy, confirmation, authorization, execution, and verification.

No unrestricted generic action executor is introduced merely to make the path appear complete.

### OPS-04 live implementation

Planned ACTION requests now cross the existing capability boundary instead of receiving a generic executable action surface.

```
ACTION
  ↓
cognitive goal / desired outcome
  ↓
capability discovery + selection
  ↓
argument proposal
  ↓
deterministic invocation validation
  ↓
TOOL execution plan
  ↓
plan validation → policy → confirmation / authorization
  ↓
tool policy gate → execution
```

If no registered capability matches, the operation stops at capability selection. No generic `PERFORM_ACTION` handler is introduced.

The deterministic capability selector was also hardened so punctuation is normalized and generic stopwords do not create false matches. This keeps discovery a proposal boundary rather than silently turning weak lexical overlap into agency.

### OPS-05 — Canonical Memory / Continuity

Unify conversational continuity, persistent memory, provenance, working context, and learning-facing memory state into one operational lifecycle.

### OPS-05 live implementation

Task execution now enters the existing `WorkingContextRuntime` before canonical cognition whenever persistent conversation state is available.

```
persistent conversation / memory sources
  ↓
WorkingContextRuntime
  ├─ memory context items
  ├─ provenance
  ├─ conversation state
  └─ current task
        ↓
CanonicalCognitiveRuntime
  ├─ context ids
  └─ memory ids
        ↓
reasoning / planning / proposal
        ↓
existing deterministic agency path
```

Persistent context remains evidence-bearing context, not authority or truth. Memory/context failures are exposed as `UNAVAILABLE` metadata and do not grant authorization or silently create a different execution path.

Basic session identity and conversation persistence already exist through `DurableSessionRuntime`, `SessionRuntime`, and `ConversationStore`; OPS-05 connects that persistent context to actual task cognition rather than treating it as conversation-only state.

### OPS-06 — Operation State / Control Plane

Expose the causal operation lifecycle to the human interface so the user can see what JARVIS is doing, why, what it needs, what happened, what was verified, and what was learned.

### OPS-06 live implementation

The active `JARVISRuntime` now exposes one observational control plane built from the existing M25 activity stream and session-state projector.

```
live interface request
  ↓
JARVISRuntime
  ↓
OperationalControlPlane
  ├─ RuntimeActivityStream
  └─ InterfaceSessionStateProjector
        ↓
current operation / session state
        ↓
existing UI/runtime consumers
```

The live conversational request is adapted into a `STATUS` observation envelope only for the existing activity/state infrastructure. The real task semantics remain in event metadata (`route`, `stage`, `plan_id`, capability, policy, execution status, cognitive context, and outcomes).

The control plane is observational and derived. It cannot authorize execution, execute capabilities, mutate runtime policy, persist state, establish truth, or establish certainty.

### OPS-07 — Feedback → Learning → Adaptation

Close the outcome loop from verified execution evidence into experience, learning, evaluation, bounded adaptation, and future behavior.

Learning may change behavior but may not change authority.

### OPS-07 live implementation

The live execution path now closes the operational feedback loop without creating a second authority path.

```
PlanExecutionResult
      ↓
OperationalLearningRuntime
      ├─ immutable experience
      ├─ deterministic evaluation
      └─ bounded adaptation hint
                ↓
future task cognitive context
                ↓
reasoning / planning
```

`COMPLETED` execution becomes `SUCCESS_PATTERN` / `REINFORCE_PATTERN` evidence.
`FAILED` execution becomes `FAILURE_PATTERN` / `CORRECT_PATTERN` evidence.
`BLOCKED` execution becomes `BOUNDED_BLOCK` / `PRESERVE_BOUNDARY` evidence.

The learning runtime is bounded to the live JARVIS process by default and keeps only a bounded history. Learning context is advisory evidence for future cognition; it cannot authorize retry, mutate policy, grant authority, request execution, or establish truth.

The existing M23 learning-adaptation chain remains a separate, authority-bounded evidence system for learning-state adaptation. OPS-07 does not reinterpret raw tool execution as an M23.85 application artifact.

### OPS-08 — Continuous Runtime

Integrate long-horizon work, continuation, recovery, waiting states, proactive behavior, and resumability where they materially improve real operation.

### OPS-08 live implementation

The canonical `JARVISRuntime` now owns an optional durable continuous runtime composed around the existing JARVIS processor.

```
JARVISRuntime
    ↓
OperationalContinuousRuntime
    ├─ SQLite autonomous job snapshots
    ├─ fenced durable schedules
    ├─ bounded autonomous job driver
    ├─ live JARVIS processor
    └─ background pulse loop
             ↓
       existing JARVIS
       understand → contextualize → reason → plan → capability →
       policy → confirmation/authorization → execution → learning
```

The continuous runtime does not create a second policy, capability, authorization, execution, or learning authority. Its responsibility is orchestration: persist a job, wake it, ask the existing JARVIS spine to perform one bounded cycle, persist the resulting lifecycle state, and schedule the next cycle when continuation is permitted.

Autonomous lifecycle states are durable across process restart:

- `QUEUED`
- `RUNNING`
- `WAITING_AUTHORIZATION`
- `WAITING_INPUT`
- `WAITING_TOOL`
- `PAUSED`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

Execution failures receive a bounded recovery budget before the autonomous job becomes terminal. Scheduler-level failures use fenced leases and bounded backoff rather than silently spinning.

A waiting authorization is persisted and removes the job from automatic scheduling. Resumption requires the existing explicit confirmation boundary; restart never implies authorization or execution.

The local launcher starts the continuous runtime by default. Set `JARVIS_AUTONOMOUS_RUNTIME=0` to disable the background pulse loop, or use `JARVIS_AUTONOMOUS_POLL_SECONDS` to adjust cadence.

The runtime is intentionally available through the canonical facade:

```
runtime.submit_autonomous(...)
runtime.inspect_autonomous(...)
runtime.resume_autonomous(...)
runtime.cancel_autonomous(...)
runtime.tick_autonomous(...)
```

This creates the operational condition the project was missing: JARVIS can remain alive and perform durable bounded work while the architecture continues evolving.

Integrate long-horizon work, continuation, recovery, waiting states, proactive behavior, and resumability where they materially improve real operation.

### OPS-09 — Operator / Control Surface

Make the durable runtime directly driveable and observable through the existing human operator and cockpit surfaces.

### OPS-09 live implementation

Operator commands now delegate to the canonical JARVISRuntime autonomous facade:

```
:work <goal>
:jobs
:job <job-id>
:resume <job-id> confirm
:resume <job-id> {"key":"value"}
:cancel <job-id>
```

These are interface mechanics only. They do not bypass the canonical task path, policy, authorization, confirmation, capability realization, execution, verification, or learning boundaries.

The control-plane snapshot now includes bounded autonomous-job projections containing identity, goal, lifecycle state, progress, waiting/result/failure summaries, and explicit false authority flags. Working context is not projected.

```
operator / cockpit
       ↓
JARVISRuntime autonomous facade
       ↓
OperationalContinuousRuntime
       ↓
durable autonomous state
```

This closes the practical loop required by the operational strategy: JARVIS can be left working while development continues, and the operator can inspect, resume, or cancel that work without introducing a second runtime authority.

### OPS-11 — Autonomous Learning Continuity

Operational learning now survives autonomous processor reconstruction through the existing persistent-intelligence repository.

```
execution outcome
      ↓
OperationalLearningRuntime
      ├─ immutable experience
      ├─ deterministic evaluation
      ├─ bounded adaptation hint
      └─ candidate episodic persistence
                ↓
fresh JARVIS processor
                ↓
hydrate advisory learning evidence
                ↓
cognition / advisory plan
```

Learning evidence is persisted as `EPISODIC` + `CANDIDATE` state with explicit experience provenance. It is never promoted to active memory automatically and cannot become policy, authorization, retry permission, execution, or truth.

Every launcher-created processor uses the same SQLite-backed `PersistentMemoryRepository`, while each processor receives its own bounded `OperationalLearningRuntime` instance hydrated from that repository.

Fresh autonomous processors therefore retain prior outcome-derived guidance without sharing mutable runtime state or creating a second authority path.

### Exact OPS-11 verification

Final feature head:
`76ba21334885321ed1ead9a511345882b7fe4f2a`

Fresh exact-head verification PR #456:
- Deployment Closure Verification #175 — **SUCCESS**
- Backend core regression: **3338/3338 OK**
- UI install/build — **SUCCESS**
- Deployment Acceptance #131 — **SUCCESS**
- CS8 Boundary Red-Team #154 — **SUCCESS**
- CS9 Architecture Cleanup + Regression #142 — **SUCCESS**

Temporary verifier PRs #454, #455, and #456 were closed unmerged after their receipts.

### OPS-12 — Durable Authorization Reconciliation

Authorization waiting is now restart-safe across the autonomous control plane.

An autonomous job stores its pending JARVIS operation ID in durable working context. If the runtime process restarts, the volatile confirmation map is gone, but `reconcile_confirmation()` now searches persisted `WAITING_AUTHORIZATION` jobs for the operation ID before synchronizing a completed confirmation.

```
durable WAITING_AUTHORIZATION job
        ↓
process restart
        ↓
normal JARVIS confirmation executes
        ↓
durable pending operation ID lookup
        ↓
autonomous job → COMPLETED
```

The reconciliation path never authorizes an operation itself. It only synchronizes durable autonomous state after the existing confirmation/authorization/execution boundary has already completed.

### Exact OPS-12 verification

Feature head:
`ccfd316d770525d46fe042914055925075ed128a`

Fresh exact-head verification PR #458:
- Deployment Closure Verification #180 — **SUCCESS**
- Backend core regression: **3339/3339 OK**
- UI install/build — **SUCCESS**
- Deployment Acceptance #136 — **SUCCESS**
- CS8 Boundary Red-Team #159 — **SUCCESS**
- CS9 Architecture Cleanup + Regression #147 — **SUCCESS**

Temporary verifier PR #458 was closed unmerged.

### OPS-13 — Durable Lifecycle Self-Healing

The autonomous runtime now treats durable job state and scheduler state as a recoverable pair rather than assuming every write boundary succeeds perfectly.

Safe reconciliation rules:

- `QUEUED` jobs without a schedule are requeued at the next reconciliation point.
- `WAITING_*` and terminal jobs have stale schedules removed.
- schedules whose job no longer exists are deleted.
- `RUNNING` jobs are not blindly resurrected; that avoids duplicating active work after an ambiguous crash.
- explicit cancellation removes its schedule immediately.

```
durable jobs ↔ durable schedules
       ↓
reconcile_durable_state()
       ├─ restore safe queued work
       ├─ remove stale scheduling
       └─ preserve running-work safety
```

### Exact OPS-13 verification

Feature head:
`5ee341374b5b993c14a50c38c4ff6a6073845a70`

Fresh exact-head verification PR #460:
- Deployment Closure Verification #188 — **SUCCESS**
- Backend core regression: **3342/3342 OK**
- UI install/build — **SUCCESS**
- Deployment Acceptance #144 — **SUCCESS**
- CS8 Boundary Red-Team #167 — **SUCCESS**
- CS9 Architecture Cleanup + Regression #155 — **SUCCESS**

Temporary verifier PR #460 was closed unmerged.

### OPS-14 — Lease-Safe Long-Running Execution

Scheduler ownership is now renewable for the full duration of a long autonomous execution pulse.

The durable scheduler claim remains fenced by its exact claim token. A heartbeat renews the lease while the worker is executing, preventing an active pulse from silently outliving its ownership window.

Critically, lease loss is terminal for that scheduler claimant: once renewal is rejected or the lease expires, that claimant cannot mutate the schedule. Durable lifecycle reconciliation owns the subsequent recovery.

```
claim
  ↓
renew ownership while executing
  ↓
execution completes
  ↓
fenced completion

or

lease lost
  ↓
no schedule mutation
  ↓
reconciliation / later safe recovery
```

### Exact OPS-14 verification

Repaired feature head:
`9b060819cc4285f8571aa3ef14b2df0577e02381`

Fresh exact-head verification PR #463:
- Deployment Closure Verification #198 — **SUCCESS**
- Backend core regression: **3345/3345 OK**
- UI install/build — **SUCCESS**
- Deployment Acceptance #154 — **SUCCESS**
- CS8 Boundary Red-Team #177 — **SUCCESS**
- CS9 Architecture Cleanup + Regression #165 — **SUCCESS**

Temporary verifier PRs #462 and #463 were closed unmerged.

## Operational acceptance

Operationalization is complete only when real end-to-end scenarios demonstrate the living loop.

Required scenario classes:

1. persistent memory across restart;
2. useful read/discovery work;
3. confirmed state-changing work;
4. execution failure and bounded recovery;
5. long-horizon work across restart;
6. outcome-driven learning that changes later behavior without expanding authority.

The final acceptance trace is:

```
USER
 ↓
UNDERSTAND
 ↓
REMEMBER
 ↓
REASON
 ↓
PLAN
 ↓
PROPOSE
 ↓
AUTHORIZE
 ↓
ACT
 ↓
OBSERVE
 ↓
VERIFY
 ↓
LEARN
 ↓
IMPROVE
 ↓
USER BECOMES MORE CAPABLE
```

Passing these scenarios marks the end of the pre-operational assembly program.

After that point, architecture evolves through use:

```
USE → OBSERVE → IMPROVE → USE BETTER
```

## Engineering workflow

The operationalization program follows the project rule:

```
READ THE WHOLE BOUNDARY
→ UNDERSTAND THE WHOLE SYSTEM
→ DESIGN THE COMPLETE BOUNDARY GRAPH
→ IMPLEMENT THE ENTIRE BOUNDARY
→ INTEGRATE
→ TEST AT THE MILESTONE BOUNDARY
→ REPAIR
→ RETEST
→ RECEIPT
→ NEXT BOUNDARY
```

No merge is implied by completion of a boundary. Pull requests remain reviewable and unmerged until explicitly requested.
