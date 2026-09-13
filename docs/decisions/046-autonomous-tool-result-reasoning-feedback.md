# Decision 046 — Autonomous Tool Result Reasoning Feedback

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a provider-neutral feedback adapter that converts an executed `ToolResult` into bounded reasoning context for the next autonomous cycle.

The adapter:

- accepts only a validated `ToolResult`;
- preserves tool identity and invocation identity;
- records success/failure explicitly;
- exposes returned content or structured error information as observation data;
- never executes another tool;
- never mutates an `AutonomousJob`, persistence, authorization, or provider state.

## Reasoning boundary

A tool result is an observation, not truth. The next reasoning cycle may interpret the observation, revise its hypothesis, request another tool, wait for authorization/input, complete, or fail.

## Safety boundary

- tool success is not semantic truth;
- tool failure is not automatically a job failure;
- feedback does not grant permission;
- feedback does not authorize retries;
- feedback is deterministic data supplied to the next reasoning cycle.
