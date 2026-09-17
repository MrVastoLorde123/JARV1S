# Decision — Phase 8 Goals, Planning, and Decision Support

## Decision

Introduce a provider-neutral planning decision subsystem between bounded reasoning and downstream initiative/authority.

## Rationale

JARVIS already has older execution-plan and proactive initiative artifacts. The missing architectural layer is the deterministic bridge that binds a current world/reasoning context to a goal, compares multiple candidate plans, represents blockers and ambiguity, and emits an advisory plan selection without authorizing it.

The new subsystem therefore reuses upstream world and reasoning identity while keeping existing execution and initiative systems separate.

## Invariants

1. Goal expresses desired outcome, not authorization.
2. Planning context binds one goal to one world snapshot and one reasoning result.
3. Candidate steps are descriptive and contain no executable callable surface.
4. Ambiguity becomes `REVIEW`, not certainty.
5. Blocked plans remain inspectable and cannot become the advisory selection.
6. Ranking is deterministic.
7. Plan selection is advisory and never creates permission, confirmation, authorization, provider choice, or execution.
8. The planning runtime does not persist state or mutate the external world.

## Non-goals

This phase does not execute plans, modify policy, add external model providers, replace the existing initiative proposal chain, or merge branches.
