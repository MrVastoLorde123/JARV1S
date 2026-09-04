# M17 — Human Operating Layer

## Goal

Give JARVIS a persistent, human-driveable operating surface without creating a second semantic or authority engine.

The human operating layer owns interaction mechanics. JARVIS continues to own reasoning, interpretation, context, policy, authorization, execution, recovery, and all existing semantic boundaries.

## Operating model

```text
Human
  ↓
Human Operating Layer
  ↓
Interface Boundary
  ↓
JARVISRuntime
  ↓
existing JARVIS semantics
```

The local CLI is one interface surface, not JARVIS itself.

## M17 slices

### M17.1 — Operator Boundary

Introduced `HumanOperatingLayer` as the human-facing control boundary.

Contract:

```text
Interface control ≠ JARVIS semantics
Interface control ≠ authorization
Interface control ≠ execution
```

### M17.2 — Persistent Interaction

The operator remains alive for repeated requests instead of executing one hard-coded prompt.

### M17.3 — Session Driveability

Every normal request carries a stable session ID for the lifetime of the operator process. An explicit session ID can be supplied for durable conversation continuity.

```text
session identity ≠ authority
session continuity ≠ approval
```

### M17.4 — Local Control Commands

```text
:help
:session
:new
:quit
```

These commands remain local to the operating layer and cannot grant authority, authorization, or execution permission.

### M17.5 — Request Sequencing

Each normal human request receives a request ID and travels through the existing interface boundary and canonical runtime.

### M17.6 — Local Runtime Integration

`src/run_local_jarvis.py` starts the Human Operating Layer instead of submitting a hard-coded prompt. The launcher may provide `JARVIS_SESSION_ID` for durable session continuity.

### M17.7 — Human Operating Contract Tests

Tests cover normal delegation, stable session identity, local command isolation, session replacement, quit/empty-input behavior, repeated interaction, and invalid runtime contracts.

## Authority walls

```text
Input ≠ Authorization
Selection ≠ Approval
Approval ≠ Authorization
Conversation ≠ Policy
Interface ≠ Authority
Session ≠ Authority
Response ≠ Execution
Human Operating Layer ≠ JARVIS
```

Existing authority remains the only authority path.

## Completion condition

M17 is complete when a human can run JARVIS continuously from a supported interface, send multiple requests, maintain or explicitly replace session identity, control the session locally, and do so without bypassing the canonical runtime or authority chain.

## Current status

**IMPLEMENTED — awaiting local focused + core + interactive receipt.**

M17 makes JARVIS driveable. It does not by itself make JARVIS continuously self-directing; M15 initiative machinery and M16 controlled self-development machinery remain separate capabilities for later integration.
