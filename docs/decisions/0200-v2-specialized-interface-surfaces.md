# Decision 0200 — V2 Specialized Interface Surfaces

**Status:** IMPLEMENTED IN M27.6 / AWAITING LOCAL VERIFICATION

M27.6 establishes specialized interface surfaces instead of treating every task as generic chat. Conversation remains general intelligence; Workspace is a literal folder-rooted environment for inspect/generate/edit/verify workflows; Research is a topic-and-evidence environment centered on engineering and thinking; Planning is a structured outcome-to-execution workbench.

Work exposes current runtime state and introduces a user-facing pause/resume concept so guidance, feedback, commands, or boundaries can be supplied before continuation. The UI never becomes execution authority; pause/resume must eventually travel through the existing backend authority and execution boundaries.

SELF and CAPABILITIES are intentionally expansive surfaces and should grow with models, plugins, integrations, workers, memory, learning, diagnostics, configuration, and explanations. HOME remains the living cockpit and is deliberately left open for a stronger unique identity in a later iteration.

## Invariants

- Specialized UI surfaces are capabilities of the interface, not authorities.
- Workspace selection does not imply authorization to mutate arbitrary files.
- Research presentation is evidence/context, not truth by itself.
- Planning artifacts remain proposals until backend authority boundaries accept them.
- Pause/resume does not bypass confirmation, policy, authorization, or execution integrity.
- SELF and CAPABILITIES can expose system detail without redefining core semantics.
- The gateway remains the replaceable boundary between the renderer and JARVIS Core.
