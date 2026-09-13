# Decision 046 — Reasoning Tool Feedback Cycle Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a coordinator that connects the existing reasoning worker, reasoning tool-action gate, and tool-result feedback adapter for one bounded autonomous cycle.

The coordinator:

- obtains one `AutonomousReasoningAction` through the existing reasoning worker;
- sends `TOOL_REQUEST` actions through the existing M61 gate;
- returns `WAIT_TOOL` when authorization/confirmation is still required;
- converts an executed `ToolResult` through the existing M62 feedback adapter;
- returns a `CONTINUE` cycle result containing bounded observation/context for the next reasoning pass;
- delegates non-tool reasoning dispositions back to the existing M59 cycle contract.

## Safety boundary

- The coordinator does not grant authorization.
- `confirmed=True` is an explicit runtime input and is not inferred from model output.
- Tool execution remains owned by M61 and `ToolService`.
- Tool results are observations, not semantic truth.
- No persistence, provider selection, retry policy, or hidden execution authority is introduced.
