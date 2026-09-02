# JARVIS

> **Third-Hand and Second-Brain**

JARVIS is a personal intelligence and agency system designed to help its user turn thoughts into words, words into plans, and plans into real-world outcomes.

JARVIS is **the system**. AI models, tools, plugins, workers, storage systems, and interfaces are capabilities inside it—not authorities over it.

## Current Milestone

**M8 — Agency / Execution: VERIFIED / COMPLETE**

The M8 implementation is verified at **942 / 942 tests passing** from the user's real checkout.

```text
M7 Authority
      ↓
ExecutionRequest
      ↓
M8.1 Runtime
      ↓
M8.2 Capability / Plugin Boundary
      ↓
M8.3 Observation Integration
      ↓
M8.4 Lifecycle / Continuation
      ↓
M8.5 Controlled Multi-Step Agency
      ↓
M8.6 Reliability / Recovery
```

### M8 invariants

```text
READY ≠ EXECUTED
Execution ≠ Authorization
Observation ≠ Permission
Sequencing ≠ Authority
Continuation ≠ Authorization
Recovery ≠ Authorization
Retry Eligibility ≠ Permission
```

M8.6 completes the agency runtime without introducing a second authority system. Recovery remains bounded, explicit, and non-executing; any new executable action still requires a fresh M7 authority path.

## Road Ahead

```text
M6  Working Context            ✅
M7  Deterministic Authority    ✅ CLOSED
M8  Agency / Execution         ✅ CLOSED
M9  Workforce / Delegation     → next
M10 Intelligence / Learning
M11 Interface / Experience
```

The milestone labels are directional. The architectural boundary is the contract.

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Authority Architecture](docs/architecture/authority.md)
- [Agency Architecture](docs/architecture/agency.md)
- [Milestone Architecture](docs/architecture/milestones.md)
- [M7 Complete](docs/milestones/M7_COMPLETE.md)
- [M8.6 Reliability / Recovery](docs/milestones/M8_6_AGENCY_RELIABILITY_RECOVERY.md)
- [Architecture Decisions](docs/decisions/)
