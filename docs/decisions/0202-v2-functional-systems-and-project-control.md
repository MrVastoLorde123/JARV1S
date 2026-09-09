# Decision 0202 — V2 Functional Systems and Project Control

**Status:** IMPLEMENTED IN M27.9 / AWAITING LOCAL VERIFICATION

## Purpose

Every primary interface surface must represent a meaningful system. UI elements exist to inspect, create, control, understand, or communicate with JARVIS systems rather than decorate the interface.

## Projects

The former WORK surface is renamed PROJECTS. A project is an editable JARVIS work object with identity, progress, state, workspace, current operation, plans, feedback, guidelines, boundaries, and runtime control.

Project progress may be paused and resumed. Pausing is a user-facing control concept and must eventually map through backend authority and execution boundaries.

Projects may be initiated through commands from Chat. Project initiation may create or attach a workspace and begin the appropriate procedures.

## Chat systems

### Conversation
General conversation with a dedicated conversation history.

### Workspace
A literal directory-rooted environment where JARVIS can inspect, generate, edit, code, and verify. A workspace can be created or selected and may become the working context of a project.

### Research
An engineering think tank for topics, sources, evidence, brainstorming, comparison, challenge, and deliberate thinking. Research history is separate from Conversation history.

### Planning
A planning and automation environment for defining outcomes, steps, dependencies, checkpoints, boundaries, readiness, and future execution. Plans may describe direct JARVIS work or recurring automation such as scraping, monitoring, and information gathering.

## Home

HOME is the awareness and orientation layer. It surfaces what matters now, what changed, what needs the user's attention, current system activity, projects, device specifications, and model assignments. HOME does not absorb MIND's purpose.

## Mind

MIND remains a dedicated core environment for JARVIS's internal world. It is expected to contain explorer, graph, thinking, memory, context, plans, learning, evidence, relationships, and future cognitive structures. It is not a landing page.

## Capabilities and Self

CAPABILITIES and SELF remain intentionally expansive. Their contents may grow as JARVIS gains skills, plugins, models, integrations, workers, diagnostics, explanations, and other systems.

## Architectural invariants

- UI elements must have functional meaning.
- Interface state does not grant authority.
- Workspace selection does not itself authorize arbitrary mutation.
- Project controls do not bypass policy, authorization, confirmation, or execution integrity.
- Research output is evidence/context, not truth merely because it is displayed.
- Planning artifacts remain proposals until backend authority accepts them.
- Chat surface histories remain semantically separated.
- MIND remains separate from HOME awareness.
- The replaceable gateway remains the renderer/Core boundary.
