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
