# Decision 045 — Reasoning Tool Action Gate

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a deterministic gate between an autonomous reasoning `TOOL_REQUEST` and the existing `ToolService`.

The gate:

- converts a validated `AutonomousReasoningAction` into an existing `ToolRequest`;
- resolves the declared `ToolDefinition` through the existing `ToolRegistry`;
- stops with an explicit authorization-required result when the tool declares `requires_confirmation=True` and no explicit confirmation has been supplied;
- invokes the existing `ToolService` only when the request is executable under the declared tool contract or an explicit confirmation has been supplied;
- returns the existing `ToolResult` without interpreting it as truth or authorization.

## Safety boundary

- model output is a proposal, not permission;
- capability discovery is not permission;
- the gate does not manufacture authorization;
- explicit confirmation is an input to this boundary, not something inferred from the model;
- tool execution remains owned by `ToolService`;
- no persistence or autonomous-job mutation occurs inside the gate.
