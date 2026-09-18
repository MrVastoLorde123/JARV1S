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

### OPS-05 — Canonical Memory / Continuity

Unify conversational continuity, persistent memory, provenance, working context, and learning-facing memory state into one operational lifecycle.

### OPS-06 — Operation State / Control Plane

Expose the causal operation lifecycle to the human interface so the user can see what JARVIS is doing, why, what it needs, what happened, what was verified, and what was learned.

### OPS-07 — Feedback → Learning → Adaptation

Close the outcome loop from verified execution evidence into experience, learning, evaluation, bounded adaptation, and future behavior.

Learning may change behavior but may not change authority.

### OPS-08 — Continuous Runtime

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
