# JARVIS Documentation

This directory contains the architectural documentation, milestone records, and Architecture Decision Records (ADRs) for JARVIS.

## Current Status

**M7 — Deterministic Authority Pipeline: CLOSED**

M7 ends at a provider-neutral execution handoff. The system can establish that an action is authorized and integrity-valid without allowing the semantic layer itself to execute it.

Verified state at M7.10: **884 / 884 tests passing**.

## Architecture Guides

- [Architecture Overview](architecture/overview.md) — core subsystem boundaries and principles
- [Authority Architecture](architecture/authority.md) — deterministic authority and provenance pipeline
- [Agency Architecture](architecture/agency.md) — the M8 execution/agency boundary
- [Milestone Architecture](architecture/milestones.md) — current and planned architectural progression
- [AI Architecture](architecture/ai.md) — provider-neutral intelligence layer
- [Context Architecture](architecture/context.md) — context acquisition and composition
- [Memory Architecture](architecture/memory.md) — memory formation, retrieval, and evidence

## Milestones

- [M7 Complete](milestones/M7_COMPLETE.md) — final M7 scope and closure boundary

Earlier milestones remain represented by their implementation and ADR history.

## Architecture Decision Records

The `decisions/` directory contains the durable ADR record. ADRs are historical contracts and should be read together with the current architecture guides.

## Development Guides

Development and testing guides should describe the actual repository workflow and may evolve as the runtime architecture evolves.

## Documentation Rules

Documentation should:

1. describe the architecture that actually exists;
2. distinguish implemented behavior from future intent;
3. identify hard boundaries and invariants explicitly;
4. never imply that model output is equivalent to authority or truth;
5. preserve milestone closure instead of inventing work to extend a milestone.
