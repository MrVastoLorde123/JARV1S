# Decision 012 — Capability Invocation Boundary

## Status
Accepted

## Context

Capability selection can identify a tool, but selection must not itself execute a tool. The selected capability also declares an input schema that can catch malformed arguments before the request reaches policy and execution.

## Decision

Introduce `CapabilityInvocationBuilder` as a small provider-neutral boundary that:

1. accepts a `ToolDefinition` and argument mapping;
2. validates required arguments and supported primitive JSON-schema-like types;
3. creates a `ToolRequest` with optional invocation and request metadata;
4. never invokes tools;
5. never makes policy or confirmation decisions.

Unknown arguments are preserved rather than rejected at this layer. Capability-specific handlers remain responsible for their own detailed semantics, while the policy gate remains the final authorization boundary.

## Resulting flow

`natural language -> capability selection -> invocation construction/validation -> execution plan -> policy -> confirmation -> tool gate -> tool service`

This keeps the model free to propose structured arguments while ensuring the executable request is materialized only by a deterministic system component before authorization.
