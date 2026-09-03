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

```text
Experience
    ↓
Evidence + Outcome
    ↓
Evaluation
    ↓
Reasoning Quality Assessment
    ↓
Feedback Signal
    ↓
Adaptation Proposal
    ↓
Explicit Acceptance
    ↓
Bounded Preference / Behavior
    ↓
Memory Candidate
    ↓
Explicit Consolidation
    ↓
Durable Knowledge
    ↓
Reliability Assessment
    ↓
RETAINED / WATCH / CONFLICTED / SUSPENDED / REVERSED / SUPERSEDED
    ↓
Intelligence Context
    ↓
Future Reasoning
    ↓
M7 Authority
```

**Status: VERIFIED / COMPLETE.**

## M11 — Interface / Experience

M11 exposes JARVIS through replaceable interaction surfaces without making an interface the system itself.

```text
Interface Surface
      ↓
Interface Boundary
      ↓
Session / Conversation
      ↓
Request Bridge
      ↓
Streaming / Multi-Modal / HITL Experience
      ↓
Reliability / Recovery
      ↓
JARVIS
```

M11 preserves the distinction between interface transport and system authority.

```text
Interface ≠ JARVIS
Channel ≠ Authority
Input ≠ Authorization
Response ≠ Execution
Human Input ≠ Authorization
Recovery ≠ Authorization
Provider ≠ JARVIS
```

**Status: VERIFIED / COMPLETE.**

## M12 — System Integration / Orchestration

M12 integrates the bounded M11 transport layer with the existing JARVIS semantic, durable-session, event, and recovery systems into one application-facing runtime.

```text
M11 Transport
     ↓
Unified Request
     ↓
Session / Durable Session
     ↓
System Runtime
     ↓
Event Integration
     ↓
Recovery Integration
     ↓
Canonical JARVIS Runtime
     ↓
Existing JARVIS Semantics
     ↓
M7 Authority → M8 Agency
```

### M12.1 — Unified Request Runtime

Routes a provider-neutral `JARVISRequest` into the existing JARVIS processor without interpreting metadata as intent or authority.

### M12.2 — Session Runtime Binding

Binds session identity to an isolated processor while keeping session identity outside semantic query content.

### M12.3 — System Runtime Facade

Composes interface, request, and session routing into one system boundary.

### M12.4 — Durable Session Lifecycle

Persists stable session/conversation identity and permits continuity across runtime restarts.

### M12.5 — Event Integrated Runtime

Adds ordered interface response lifecycle events without changing semantic behavior.

### M12.6 — Recovery Integrated Runtime

Adds bounded transport recovery state. Retry/resume/replay remain mechanical actions, not permission or authorization.

### M12.7 — Canonical JARVIS Runtime Facade

Defines the application-facing `receive/process/respond` composition root over the verified integration stack.

### M12.8 — Application Runtime Entrypoint

Routes the local application entrypoint through the canonical runtime rather than bypassing it.

### M12.9 — End-to-End Runtime Integration

Verifies a real JARVIS processor across the complete runtime stack, including durable-session continuity, runtime restart, event ordering, recovery state, and session-identity isolation.

**M12 Status: VERIFIED / COMPLETE.**

Verified receipts:

```text
M12.7 focused      11/11
Core regression    478/478
M12.8 focused       2/2
Core regression    480/480
M12.9 focused       4/4
Core regression    484/484
```

M12 architectural invariants:

```text
Integration ≠ New Authority
Session Identity ≠ Semantic Intent
Events ≠ Execution
Recovery ≠ Permission
Runtime Facade ≠ Semantic Engine
AI Provider ≠ JARVIS Authority
```

## Architectural Direction

```text
M6  Context                       ✅ CLOSED
 ↓
M7  Deterministic Authority      ✅ CLOSED
 ↓
M8  Agency / Execution           ✅ CLOSED
 ↓
M9  Workforce / Delegation       ✅ CLOSED
 ↓
M10 Intelligence / Learning     ✅ CLOSED
 ↓
M11 Interface / Experience      ✅ CLOSED
 ↓
M12 System Integration          ✅ CLOSED
```

The sequence is deliberate: first establish what JARVIS knows, then what it is permitted to do, then how it acts, how it scales work, how intelligence improves, how the human experiences it, and finally how those bounded systems compose into one application-facing runtime.

Final hardening is intentionally separate from architectural integration. Database isolation/leak prevention, persistence security, filesystem boundaries, credential handling, concurrency, and broader security review will be handled as a dedicated hardening phase rather than mixed into completed milestone semantics.
