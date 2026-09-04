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

```text
You → request → JARVIS → response
You → request → JARVIS → response
You → request → JARVIS → response
```

### M17.3 — Session Driveability

Every normal request carries a stable session ID for the lifetime of the operator process. An explicit session ID can be supplied to resume an existing durable conversation identity.

```text
session identity ≠ authority
session continuity ≠ approval
```

### M17.4 — Local Control Commands

The operator owns a minimal set of explicit local commands:

```text
:help
:session
:new
:quit
```

These commands do not enter JARVIS reasoning and cannot grant permission, authorization, or execution authority.

### M17.5 — Request Sequencing

Each human request receives a unique request ID and is sent through the existing interface boundary into the canonical runtime.

No alternate processing path is introduced.

### M17.6 — Local Runtime Integration

`src/run_local_jarvis.py` now starts the Human Operating Layer, and `scripts/run_jarvis.ps1` exposes an optional durable session ID.

### M17.7 — Human Operating Contract Tests

Tests verify that:

- normal text reaches the canonical runtime shape;
- the session ID is preserved;
- local commands do not reach the runtime;
- starting a new session changes identity only;
- quit remains local control;
- empty input is not submitted.

## Authority walls

The Human Operating Layer must never imply:

```text
Input = Authorization
Selection = Approval
Approval = Authorization
Conversation = Policy
Interface = Authority
Session = Authority
Response = Execution
Human Operating Layer = JARVIS
```

Existing authority remains the only authority path.

## M17 completion condition

M17 is complete when a human can run JARVIS continuously from a supported interface, send multiple normal requests, maintain session identity, explicitly control the session, and do so without bypassing the canonical runtime or authority chain.

## Next capability boundary

M17 makes JARVIS driveable.

It does not yet make JARVIS continuously self-directing.

M16 provides controlled self-development machinery. M15 provides initiative machinery. Future proactive/continuity milestones can connect those mechanisms into longer-horizon autonomous operation while preserving the authority walls.
