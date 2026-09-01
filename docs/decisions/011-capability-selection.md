# Decision 011 — Capability Selection Boundary

**Status:** Accepted

## Context

JARVIS can now discover registered tool definitions and execute explicit tool
requests through the existing policy and confirmation boundary. The next step
is allowing an intelligence layer to determine which capability is relevant
to a user's intent.

Selection must not become an execution authority, and the core orchestrator
must not accumulate tool-specific knowledge.

## Decision

Introduce three provider-neutral layers:

```text
CapabilityCatalog
      ↓
CapabilitySelector
      ↓
CapabilitySelectionService
```

- `CapabilityCatalog` exposes an immutable snapshot of registered
  `ToolDefinition` values.
- `CapabilitySelector` ranks candidate capabilities for an intent.
- `CapabilitySelectionService` composes discovery and ranking into one
  application-facing service.

The selector returns proposals only. It does not construct a privileged
execution path and does not invoke tools.

A dependency-free deterministic selector is the V1 fallback. A future
model-backed selector may implement the same `CapabilitySelector` protocol
without changing the execution stack.

## Consequences

Positive:

- JARVIS can reason about available capabilities without importing concrete
  tool implementations.
- The future LLM selector is replaceable and testable in isolation.
- Selection cannot bypass `PolicyGate` or confirmation by construction.
- Tool expansion remains plugin-oriented.

Trade-off:

- V1 still requires a later layer to turn a selected capability into a
  validated `ToolRequest` with arguments. That is intentional; argument
  generation and execution authorization remain separate responsibilities.
