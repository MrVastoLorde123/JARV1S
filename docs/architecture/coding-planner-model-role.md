# Coding Planner Model Role

The coding planner is an explicit `CODING` cognitive boundary.

```text
CodingAgentTask
      |
      v
AICodingAgentPlanner
      |
      | generate_for_role(CODING)
      v
AIService
      |
      v
ModelRoutingRuntime
      |
      +-- observed availability
      +-- explicit role policy
      +-- deterministic model selection
      |
      v
LocalProvider generation
```

The planner may select a model for coding cognition, but the selected model receives no authority, permissions, tools, execution rights, or verification truth from that selection.

The planner remains responsible only for converting the model response into a bounded `CodingAgentPlan`. Existing confirmation, tool authorization, execution, and verification boundaries remain outside the model role-selection operation.

A legacy AI-service-like object without `generate_for_role()` may still be used by compatibility tests; production `AIService` exposes the role-routing surface.
