# M28.10 — Agent Entity Lifecycle and Worker Instantiation

## Decision
Researcher-07 is not a permanent built-in character. It is a prototype name for a dynamically instantiated agent entity that JARVIS may create when a task benefits from delegated work.

## Contract
- Agents are runtime entities created by JARVIS from an agent role/archetype and a specific assignment.
- A concrete agent gets a stable identity for the lifetime of its active work lineage, such as `Researcher-07`.
- The identity is evidence of an entity instance, not a fixed personality that permanently exists in the world.
- JARVIS decides whether an agent should exist at all. Simple work may remain native to JARVIS with no worker instantiated.
- An agent may have a lifecycle such as CREATED → ASSIGNED → TRAVELLING → EXECUTING → RETURNING → HANDOFF → RETIRED.
- Agent state must reference its assignment, current landscape/location, selected model, capabilities being used, produced evidence, and result handoff.
- The world should show active agents spatially. Retired agents may leave history or archival traces without remaining as active clutter.
- Agent visualization is derived from backend state; the UI must not fabricate an agent simply because a visual component exists.

## Initial entity boundaries
The first backend contract should establish:
- `AgentContract`: identity, archetype/role, status, current landscape, assignment id, model id, capability ids, timestamps.
- `AgentRoute`: ordered landscape transitions and current destination.
- `WorkLineage`: user intent → plan → agent assignment → model execution → evidence → synthesis/handoff.
- `EvidenceBundle`: source/evidence references generated during work, with provenance and citation metadata.
- `DiscoveryGraph`: typed concepts and relationships created or strengthened by assimilation.
- `AgentHandoff`: result, evidence references, destination, acceptance state, and completion timestamp.

## UI rule
The UI will not implement fake Researcher-07 behavior ahead of these contracts. Once the backend can emit the lifecycle, the world will render the agent moving through the corresponding landscapes.

## Boundaries
Agent existence, assignment, execution authority, model selection, capability permission, evidence validity, and handoff acceptance remain backend-controlled. Visualization is observational and does not itself authorize work.
