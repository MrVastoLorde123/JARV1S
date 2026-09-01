# Decision 009 — Tool Capability Bridge

## Context

JARVIS already has two distinct execution layers:

- core planning / validation / execution
- tool registration / policy / confirmation / invocation

`TaskType.TOOL` existed in core, but V1 planning only labeled a step `USE_TOOL`. There was no explicit bridge from that plan step to the tool layer.

The first design also made both layers independently confirmation-oriented: core execution policy required confirmation for `USE_TOOL`, while the tool-layer `PolicyGate` evaluates the concrete tool's risk and confirmation requirements.

## Decision

A `USE_TOOL` plan step carries explicit, inert invocation data in plan metadata:

- `tool_name`
- `arguments`
- optional `invocation_id`

`ToolPlanStepHandler` adapts that metadata into a `ToolRequest` and delegates to an injected `ToolInvoker`.

`JARVIS` accepts that `ToolInvoker` as a single optional dependency and installs the `USE_TOOL` adapter into its existing `PlanExecutor`. JARVIS core therefore depends on one capability contract rather than concrete tool classes, workspaces, registries, or filesystem handlers.

The injected invoker should normally be the tool-layer `PolicyGate`, preserving the boundary:

```text
JARVIS
  |
  v
ExecutionPlan
  |
  v
PlanExecutor
  |
  v
ToolPlanStepHandler
  |
  v
ToolRequest
  |
  v
Tool PolicyGate
  |
  +--> policy
  +--> confirmation
  |
  v
ToolService
  |
  v
ToolHandler
```

Core execution policy treats `USE_TOOL` as allowed at the plan level. The concrete tool's `ToolDefinition` owns its risk and confirmation requirement.

This avoids a double-confirmation architecture where a low-risk read would require an unrelated core confirmation and a high-risk write could require two confirmations.

## Constraints

The planner does not inspect tool definitions or filesystem behavior. It only validates the structural shape of explicit tool-task metadata.

The adapter does not select tools, make policy decisions, or bypass confirmation.

The executor remains generic: it registers an action handler and does not know what implementation sits behind `USE_TOOL`.

`JARVIS` does not construct a default filesystem stack and does not import concrete workspace handlers. A caller supplies the capability boundary it wants JARVIS to use.

Tool-specific result semantics remain behind the tool boundary. A failed `ToolResult` is surfaced as an execution failure with its tool error code and message.

## V1 Scope

Tool selection from ordinary natural language is still intentionally out of scope. A caller must explicitly construct a `TaskRequest` with `TaskType.TOOL` and the requested tool metadata.

A future planner may derive that structure from model output, but it must continue to target this same provider-neutral contract.
