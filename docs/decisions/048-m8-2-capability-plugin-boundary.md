# Decision 048 — Capability / Plugin Execution Boundary

## Context

M7 deliberately ends at a provider-neutral, authorized `ExecutionRequest`. M8.1 executes through an injected adapter but must not decide which concrete capability or provider implements an operation.

The repository already has `ToolDefinition`, `ToolRequest`, `ToolResult`, `CapabilityCatalog`, and a validated tool stack. What is missing is an explicit ownership boundary connecting provider-neutral operations to concrete capabilities and plugins.

## Decision

Introduce a deterministic `CapabilityPluginRegistry` that owns three mappings:

```text
operation
   ↓
capability
   ↓
plugin
```

Plugins expose stable identity, declared capability definitions, and execution behavior. The registry owns discovery and binding. The plugin layer never owns policy, confirmation, authorization, authorization integrity, or continuation decisions.

## Why explicit operation bindings

`ExecutionRequest.operation` remains provider-neutral. An operation must not silently become a concrete tool name merely because one implementation currently exists.

An explicit binding makes replacement and competition possible:

```text
"read_workspace_file"
        ↓
      "read_file"
        ↓
    filesystem plugin
```

The operation is the semantic request. The capability is the declared execution surface. The plugin is the concrete implementation.

## Constraints

1. Plugin identities must be unique.
2. Capability ownership must be unique within the registry.
3. Operation bindings must reference registered capabilities.
4. Resolution is deterministic and side-effect free.
5. Plugin results must identify the capability that was actually requested.
6. Plugins may execute only; they cannot create or modify authority.
7. Dynamic code loading and arbitrary plugin installation are outside M8.2.

## Consequence

M8.2 makes the project's "everything is a plugin" direction concrete without turning plugins into a second authority system. Later milestones can use the boundary for execution-result observation, lifecycle, continuation, and controlled multi-step agency.
