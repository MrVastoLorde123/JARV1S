# JARVIS

> **Third-Hand and Second-Brain**

JARVIS is a personal intelligence and agency system designed to help its user turn thoughts into words, words into plans, and plans into real-world outcomes.

JARVIS is **the system**. AI models, tools, plugins, workers, storage systems, and interfaces are capabilities inside it—not authorities over it.

## Current Milestone

**M9 — Workforce / Delegation: M9.6 VERIFIED / COMPLETE**

The latest verified user checkout passes **986 / 986 tests**.

### M9 roadmap

```text
M9.1  Worker Identity / Assignment Boundary       ✅
M9.2  Bounded Worker Runtime                      ✅
M9.3  Worker Context / Knowledge Boundary          ✅
M9.4  Worker Reporting / Result Integration        ✅
M9.5  Delegation / Coordination                   ✅
M9.6  Workforce Reliability / Recovery            ✅
M9.7  Driveability / Objective Continuation       → next
```

### Workforce invariant

```text
JARVIS may distribute work without distributing authority.
```

### M9.6 reliability invariants

```text
Recovery ≠ Authorization
Retry Eligibility ≠ Permission
Failure Handling ≠ Authority Escalation
Worker Recovery State ≠ Global Authority
Resumption ≠ Re-Authorization
Recovery Sequencing ≠ Dependency Bypass
```

M9.6 preserves worker identity, assignment scope, delegation dependencies, and recovery provenance. Recovery remains non-executing; any retry or follow-up execution must re-enter the established M7/M8 authority path.

## Road Ahead

```text
M6  Working Context            ✅
M7  Deterministic Authority    ✅ CLOSED
M8  Agency / Execution         ✅ CLOSED
M9  Workforce / Delegation     → M9.7
M10 Intelligence / Learning
M11 Interface / Experience
```

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Authority Architecture](docs/architecture/authority.md)
- [Agency Architecture](docs/architecture/agency.md)
- [Milestone Architecture](docs/architecture/milestones.md)
- [M7 Complete](docs/milestones/M7_COMPLETE.md)
- [M8 Complete](docs/milestones/M8_COMPLETE.md)
- [M8.6 Reliability / Recovery](docs/milestones/M8_6_AGENCY_RELIABILITY_RECOVERY.md)
- [Architecture Decisions](docs/decisions/)
