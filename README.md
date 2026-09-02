# JARVIS

> **Third-Hand and Second-Brain**

JARVIS is a personal intelligence and agency system designed to help its user turn thoughts into words, words into plans, and plans into real-world outcomes.

JARVIS is **the system**. AI models, tools, plugins, workers, storage systems, and interfaces are capabilities inside it—not authorities over it.

## Current Milestone

**M7 — Deterministic Authority Pipeline: CLOSED**

The repository's M7 implementation is verified at **884 / 884 tests passing**.

```text
Working Context
      ↓
Reasoning
      ↓
Interpretation
      ↓
Prioritization
      ↓
Proposal
      ↓
Validation
      ↓
Policy
      ↓
Confirmation
      ↓
Confirmation Integrity
      ↓
Authorization
      ↓
Authorization Integrity
      ↓
Execution Preparation / Handoff
```

The final M7 output is an execution-ready, provider-neutral handoff. **READY does not mean EXECUTED.**

## Architectural Principles

- **JARVIS is the system; AI is a capability.**
- Intelligence can propose; deterministic system boundaries decide authority.
- Provenance and identity must survive the pipeline.
- Confirmation and authorization remain explicit boundaries.
- Execution and side effects belong outside M7.
- Everything that can be added as a capability should fit the plugin model.
- Failures remain observable and cannot be reinterpreted into success.
- Provider and interface choices must not redefine core JARVIS semantics.

## Road Ahead

```text
M6  Working Context            ✅
M7  Deterministic Authority    ✅ CLOSED
M8  Agency / Execution         → next
M9  Workforce / Delegation
M10 Intelligence / Learning
M11 Interface / Experience
```

The future milestone labels are directional. The architectural boundary is the contract.

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Authority Architecture](docs/architecture/authority.md)
- [Agency Architecture](docs/architecture/agency.md)
- [Milestone Architecture](docs/architecture/milestones.md)
- [M7 Complete](docs/milestones/M7_COMPLETE.md)
- [Architecture Decisions](docs/decisions/)

## Development

M7 is a completed semantic foundation. M8 should focus on the execution runtime that consumes the M7 handoff, produces real observations/results, and preserves the same authority boundaries.
