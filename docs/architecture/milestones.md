# JARVIS Milestone Architecture

This document describes the current architectural progression. Future milestone names are directional and may be refined before implementation; the boundaries below are the important part.

## M6 — Working Context

M6 established the provider-neutral working context runtime and its composition, source selection, resolution, refresh, and consumption boundaries.

```text
Sources → Selection → Resolution → Composition → WorkingContext → AIRequest
```

## M7 — Deterministic Authority

M7 established the deterministic semantic authority pipeline and ends at an execution-ready handoff.

```text
Reason → Interpret → Prioritize → Propose → Validate → Policy
→ Confirm → Integrity → Authorize → Integrity → Prepare Handoff
```

**Status: CLOSED.** No M7.11 is required.

## M8 — Agency / Execution

M8 implements the downstream execution system that consumes `ExecutionRequest`.

The architectural focus is:

```text
ExecutionRequest
      ↓
Execution Runtime
      ↓
Capability / Plugin Resolution
      ↓
Controlled Invocation
      ↓
Observation + Result
      ↓
Verification / Failure State
      ↓
Context Update
```

M8 proves that JARVIS can drive authorized operations while preserving M7's authority boundary.

## M9 — Workforce / Delegation

The worker force belongs after a reliable single-action execution path exists.

```text
JARVIS
   ↓
Work Assignment
   ↓
Worker Runtime
   ├── research
   ├── browser / web
   ├── coding
   ├── automation
   ├── document work
   └── other capabilities
```

Workers are capability-bounded execution participants, not independent authorities. Their work remains constrained by JARVIS's execution and authorization architecture.

## M10 — Intelligence / Learning

M10 develops intelligence against the real operational history produced by JARVIS while preserving the authority architecture.

The first boundary is explicit:

```text
Memory / Observation / Outcome
              ↓
          Experience
              ↓
           Learning
              ↓
      Better Reasoning / Behavior
              ↓
          M7 Authority
```

M10.1 defines the Experience boundary before later stages decide how experiences are evaluated, consolidated, adapted, or learned from.

```text
Experience ≠ Truth
Experience ≠ Policy
Experience ≠ Authorization
Experience ≠ User Intent
Learning ≠ Authority
Confidence ≠ Certainty
Experience ≠ Execution
```

Future M10 responsibilities include:

- evidence and outcome evaluation;
- preference and behavior adaptation;
- memory consolidation and retrieval improvement;
- reasoning quality feedback loops;
- learning reliability, reversal, and integration;
- deciding when learned behavior is safe and useful to apply.

The exact model/provider strategy remains implementation detail. JARVIS remains the system; AI remains a capability.

## M11 — Interface / Experience

The interface should sit on top of JARVIS rather than define JARVIS.

```text
Voice / Text / UI / API
          ↓
       JARVIS
          ↓
   Intelligence + Agency
```

That allows the same underlying system to be driven through different interfaces without coupling authority, memory, execution, or workforce semantics to a presentation layer.

## Architectural Direction

```text
M6  Context
 ↓
M7  Authority                    ← CLOSED
 ↓
M8  Agency / Execution
 ↓
M9  Workforce / Delegation      ← CLOSED
 ↓
M10 Intelligence / Learning     ← M10.1
 ↓
M11 Interface / Experience
```

The sequence is deliberate: first establish what JARVIS knows, then what it is permitted to do, then how it acts, then how it scales work, then how intelligence improves, and finally how the human experiences the system.
