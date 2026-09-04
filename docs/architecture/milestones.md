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

## M13 — Personal Knowledge

M13 establishes structured knowledge about what memories refer to, while keeping knowledge distinct from truth, intent, policy, and authority.

```text
Memory / Evidence
       ↓
Entity Model
       ↓
People / Projects / Organizations / Systems / Concepts
       ↓
Relationships / Associations
       ↓
Persistent Personal Knowledge
       ↓
Knowledge Retrieval / Integration
```

### M13.1 — Entity Boundary

Defines immutable bounded entities as structured referents rather than truth claims.

### M13.2 — Entity Identity / Resolution

Provides deterministic resolution judgments without merging or mutating entities.

### M13.3 — Relationship Boundary

Defines bounded associations between entity identities.

### M13.4 — Evidence-Backed Associations

Connects explicit provenance to relationships without converting evidence into truth or authority.

### M13.5 — Entity Persistence

Stores and reconstructs immutable entities through a bounded persistence layer.

### M13.6 — Knowledge Retrieval

Provides deterministic read-only retrieval over persisted entities.

### M13.7 — Knowledge Integration

Composes entities, relationships, associations, persistence, and retrieval behind one knowledge-facing boundary without creating a second semantic engine.

**M13 Status: VERIFIED / COMPLETE.**

Verified receipts:

```text
M13.4 focused      14/14
M13.5 focused      13/13
M13.6 focused      14/14
M13.7 focused      14/14
Knowledge         92/92
AI                32/32
Core             484/484
```

M13 architectural invariants:

```text
Entity ≠ Truth
Entity ≠ Fact
Entity ≠ Intent
Identity ≠ Authority
Association ≠ Authorization
Association ≠ Policy
Evidence ≠ Authority
Inference ≠ Fact
Knowledge ≠ Policy
Knowledge ≠ Authorization
Knowledge ≠ User Intent
```

## M14 — Personal Context / World Model

M14 turns structured knowledge into bounded contextual state about the user's world.

```text
Entities + Relationships + Memories + Events + Current State + Goals + Temporal Context
                              ↓
                     Personal World Model
```

### M14.1 — Context State

Defines an immutable bounded representation of currently relevant context state, with source references and observation time. Context state is derived context, not truth, fact, user intent, policy, authorization, or execution permission.

**Status: IN PROGRESS.**

### Future M14 slices

- M14.2 Temporal / Historical Context
- M14.3 Goal & Project Context
- M14.4 Situational Context
- M14.5 Cross-Domain Context
- M14.6 Context Relevance / Prioritization
- M14.7 World-Model Integration

## Architectural Direction

```text
M6  Context / Working Context       ✅ CLOSED
 ↓
M7  Deterministic Authority         ✅ CLOSED
 ↓
M8  Agency / Execution              ✅ CLOSED
 ↓
M9  Workforce / Delegation          ✅ CLOSED
 ↓
M10 Intelligence / Learning        ✅ CLOSED
 ↓
M11 Interface / Experience         ✅ CLOSED
 ↓
M12 System Integration             ✅ CLOSED
 ↓
M13 Personal Knowledge             ✅ CLOSED
 ↓
M14 Personal Context / World Model  → IN PROGRESS
```

The sequence is deliberate: first establish what JARVIS knows, then what it is permitted to do, then how it acts, how it scales work, how intelligence improves, how the human experiences it, how those bounded systems compose, and then how structured knowledge becomes contextual understanding of the user's world.

Final hardening is intentionally separate from architectural integration. Database isolation/leak prevention, persistence security, filesystem boundaries, credential handling, concurrency, and broader security review will be handled as a dedicated hardening phase rather than mixed into completed milestone semantics.
