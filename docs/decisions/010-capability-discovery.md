# Decision 010 — Capability Discovery Boundary

## Context

JARVIS must eventually operate on its own workspace and other connected systems. That requires knowing which capabilities are available without teaching core about concrete tools.

The tool layer already has a registry of `ToolDefinition` objects and a `PolicyGate` that is the safe invocation boundary.

## Decision

The gated tool stack is also the capability discovery boundary.

`PolicyGate.list_definitions()` exposes a deterministic, read-only snapshot of registered `ToolDefinition` objects. `PolicyGate.invoke()` remains the only execution path.

Core may consume this boundary through the provider-neutral `ToolCapabilityGateway` protocol. `CapabilityCatalog` provides a small read-only view for discovery and exact-name lookup.

```text
JARVIS
  |
  v
ToolCapabilityGateway
  +---- list_definitions()  -> capability metadata
  |
  +---- invoke(request)     -> Policy -> Confirmation -> ToolService
```

## Constraints

Discovery must not execute tools, alter registry state, or imply permission to execute a capability.

The catalog must not contain concrete handler objects or executable behavior.

The planner remains responsible only for producing structured task plans. Capability selection can later consume the catalog, but selection must still produce an inert `ToolRequest` that passes through the existing validation and policy boundaries.

## V1 Scope

V1 exposes deterministic discovery and explicit tool invocation. Natural-language capability selection is deliberately deferred until the discovery contract is stable.

The intended future direction is that a model can inspect the capability catalog, propose a capability and arguments, and then let JARVIS validate, authorize, and execute that proposal. The model never receives direct execution authority.
