# JARVIS Documentation

This directory contains the architectural documentation, milestone records, operational guides, research studies, and Architecture Decision Records (ADRs) for JARVIS.

## Current Operational Baseline

**JARVIS V1 — OPERATIONAL / DAILY-DRIVEN FREEZE**

The current operational feature branch has crossed the pre-operational assembly boundary. JARVIS can now be driven as a living system through its canonical runtime, human operator surface, durable autonomous jobs, restart-safe lifecycle, outcome evidence, verification, and bounded learning.

- [JARVIS V1 User Guide](JARVIS_V1_USER_GUIDE.md) — detailed operator manual for daily use, autonomous work, verification, recovery, UI, and troubleshooting
- [JARVIS V1 Freeze and Post-V1 Milestone Map](JARVIS_V1_FREEZE_AND_NEXT_MILESTONE.md) — frozen baseline, V1 scope, post-V1 engineering doctrine, and candidate V2 north star
- [JARVIS Ideas Ledger](JARVIS_IDEAS_LEDGER.md) — durable archive of recovered ideas, principles, future capabilities, adjacent product concepts, and implementation status
- [JARVIS V2 Roadmap](JARVIS_V2_ROADMAP.md) — system-level roadmap from V1 freeze to Trusted Daily Agency
- [Operational JARVIS](operational/OPERATIONAL_JARVIS.md) — implementation receipts and causal-boundary history
- [Running JARVIS Locally](operations/RUNNING_JARVIS_LOCAL.md) — local startup and deployment instructions

## V2 Architecture Concepts

- [JARVIS V2 Agency Fabric](architecture/JARVIS_V2_AGENCY_FABRIC.md) — multi-agent decomposition, routing, communication, specialization, aggregation, recursion, and agency budgets
- [JARVIS Anywhere Access](architecture/JARVIS_ANYWHERE_ACCESS_CONCEPT.md) — secure remote-access architecture for continuous JARVIS availability
- [JARVIS External System Study](research/JARVIS_EXTERNAL_SYSTEM_STUDY.md) — mechanism extraction from JEV, PRAXIST, recursive-agent research, MapReduce, ticket triage, and related patterns

## Architecture Guides

- [System Map](architecture/system-map.md) — current subsystem and boundary map
- [Architecture Overview](architecture/overview.md) — core architecture and principles
- [Authority Architecture](architecture/authority.md) — deterministic authority and provenance pipeline
- [Agency Architecture](architecture/agency.md) — the M8 execution/agency boundary
- [Milestone Architecture](architecture/milestones.md) — current and planned architectural progression
- [AI Architecture](architecture/ai.md) — provider-neutral intelligence layer
- [Context Architecture](architecture/context.md) — context acquisition and composition
- [Memory Architecture](architecture/memory.md) — memory formation, retrieval, and evidence

## Milestones

- [M7 Complete](milestones/M7_COMPLETE.md) — final M7 scope and closure boundary

Earlier milestones remain represented by their implementation and ADR history. The live feature branch, implementation, tests, and verified receipts override stale historical summaries.

## Architecture Decision Records

The `decisions/` directory contains the durable ADR record. ADRs are historical contracts and should be read together with the current architecture guides.

## Development Guides

Development and testing guides should describe the actual repository workflow and may evolve as the runtime architecture evolves.

## Documentation Rules

1. Describe the architecture that actually exists.
2. Distinguish implemented behavior from future intent.
3. Identify hard boundaries and invariants explicitly.
4. Never imply that model output is equivalent to authority or truth.
5. Preserve milestone closure instead of inventing work to extend a milestone.
