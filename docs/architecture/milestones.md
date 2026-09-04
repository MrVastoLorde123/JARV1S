# JARVIS Milestone Architecture

This document describes the current architectural progression. Future milestone names are directional and may be refined before implementation; the boundaries below are the important part.

## M6 — Working Context

M6 established the provider-neutral working context runtime and its composition, source selection, resolution, refresh, and consumption boundaries.

## M7 — Deterministic Authority

M7 established the deterministic semantic authority pipeline and ends at an execution-ready handoff.

**Status: CLOSED.**

## M8 — Agency / Execution

M8 implements downstream execution of already-authorized operations through bounded capabilities/plugins.

**Status: CLOSED.**

## M9 — Workforce / Delegation

M9 adds capability-bounded workers that receive work from JARVIS without becoming independent authorities.

**Status: CLOSED.**

## M10 — Intelligence / Learning

M10 develops intelligence from operational experience while keeping learning, prediction, memory, and adaptation outside authority.

**Status: VERIFIED / COMPLETE.**

## M11 — Interface / Experience

M11 exposes JARVIS through replaceable interaction surfaces while keeping interface transport separate from semantics and authority.

**Status: VERIFIED / COMPLETE.**

## M12 — System Integration / Orchestration

M12 integrates interface, session, durable session, event, recovery, and system runtime layers into one canonical application-facing runtime.

**Status: VERIFIED / COMPLETE.**

Verified receipts included core regression through 484/484 before later schema-bootstrap integration work.

## M13 — Personal Knowledge

M13 establishes structured entities, identity resolution, relationships, evidence-backed associations, persistence, retrieval, and integration.

**Status: VERIFIED / COMPLETE.**

## M14 — Personal Context / World Model

M14 turns structured knowledge into bounded contextual state about the user's world.

```text
Entities + Relationships + Memories + Events + Current State + Goals + Temporal Context
                              ↓
                     Personal World Model
```

**Status: VERIFIED / COMPLETE.**

Key invariant: context can inform initiative but cannot become authority.

## M15 — Initiative / Proactive Agency

M15 detects opportunities/needs, evaluates them, forms proposals, schedules proactive work, and applies an initiative safety boundary before existing authority semantics.

```text
World Model
   ↓
Opportunity / Need Detection
   ↓
Initiative Candidate
   ↓
Evaluation
   ↓
Proposal
   ↓
Scheduling
   ↓
Safety Boundary
   ↓
Existing Authority Chain
```

**Status: VERIFIED / COMPLETE.**

Key invariant: initiative may produce a useful proposal, but it cannot create authority.

## M16 — Controlled Self-Development

M16 provides controlled machinery for JARVIS to change how it works without changing what it is authorized to do.

```text
Inspect → Reason → Plan → Modify → Test → Observe → Correct → Verify → Commit / Rollback
```

The milestone composes self-development proposal, impact assessment, modification planning, test verification, safe modification handoff, rollback/recovery, and integration.

**Status: VERIFIED / COMPLETE.**

Key invariant:

```text
JARVIS may change how it works
        ≠
JARVIS may change what it is allowed to do
```

## M17 — Human Operating Layer

M17 makes JARVIS continuously driveable from a supported human-facing surface without creating a second reasoning or authority path.

```text
Human
  ↓
Human Operating Layer
  ↓
Interface Boundary
  ↓
Canonical JARVIS Runtime
  ↓
Existing JARVIS Semantics
```

The first implementation is a persistent local text operator with stable session identity, unique request sequencing, explicit local control commands, and optional durable session resumption.

### M17.1 — Operator Boundary

Defines the human-facing control boundary and keeps interface mechanics separate from authority.

### M17.2 — Persistent Interaction

Keeps the local operator alive for repeated normal requests instead of issuing one hard-coded prompt.

### M17.3 — Session Driveability

Carries a stable session identity through normal requests and supports explicit durable session IDs.

### M17.4 — Local Control Commands

Provides `:help`, `:session`, `:new`, and `:quit` as interface-local controls that never grant permission or authorization.

### M17.5 — Request Sequencing

Assigns unique request IDs and routes normal human text through the existing interface boundary and canonical runtime.

### M17.6 — Local Runtime Integration

Connects `src/run_local_jarvis.py` and the PowerShell launcher to the persistent operator, including an optional session ID.

### M17.7 — Human Operating Verification

Contract tests verify normal request routing, session identity, local command isolation, session switching, quit behavior, and empty-input handling.

**Status: IMPLEMENTED — AWAITING LOCAL RUNTIME RECEIPT.**

M17 architectural walls:

```text
Interface ≠ JARVIS
Input ≠ Authorization
Session ≠ Authority
Selection ≠ Approval
Approval ≠ Authorization
Response ≠ Execution
Conversation ≠ Policy
```

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
M14 Personal Context / World Model ✅ CLOSED
 ↓
M15 Initiative / Proactive Agency  ✅ CLOSED
 ↓
M16 Controlled Self-Development    ✅ CLOSED
 ↓
M17 Human Operating Layer          → LOCAL RECEIPT
```

The sequence is deliberate: establish authority and bounded action first; then learning, interface, integration, knowledge, context, initiative, controlled self-development, and finally a human operating layer that makes those capabilities continuously usable.

M17 is driveability, not unrestricted autonomy. M15 provides initiative machinery and M16 provides controlled self-development machinery; later milestones can connect those mechanisms into longer-horizon proactive operation while preserving the authority architecture.

Final hardening remains a separate concern from milestone semantics. Database isolation/leak prevention, persistence security, filesystem boundaries, credential handling, concurrency, and broader security review will be handled as a dedicated hardening phase.
