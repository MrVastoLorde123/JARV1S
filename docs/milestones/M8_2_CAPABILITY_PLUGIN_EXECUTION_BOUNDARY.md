# M8.2 — Capability / Plugin Execution Boundary

**Status:** IMPLEMENTATION IN PROGRESS

## Purpose

M8.2 defines the boundary between provider-neutral M8 execution intent and the concrete capability/plugin that can perform it.

The core mapping is:

```text
M7 authorized ExecutionRequest
           ↓
     provider-neutral
       `operation`
           ↓
  CapabilityPluginRegistry
           ↓
       Capability
           ↓
         Plugin
           ↓
        ToolResult
```

## Responsibilities

- give plugins a stable identity and version;
- let a plugin expose one or more declared `ToolDefinition` capabilities;
- prevent duplicate plugin identities;
- prevent multiple plugins from owning the same capability name;
- bind provider-neutral M8 operations explicitly to declared capabilities;
- resolve an operation deterministically without executing anything;
- execute a resolved capability through its owning plugin;
- preserve `execution_id` as the invocation identity;
- reject plugin results that claim to belong to a different capability.

## Authority boundary

The capability/plugin layer does **not** own:

- reasoning or interpretation;
- policy decisions;
- confirmation decisions;
- authorization decisions;
- authorization integrity;
- permission escalation;
- continuation or retry policy;
- worker orchestration.

A plugin receives an `ExecutionRequest` only through the explicit M8 execution boundary. The plugin can perform the capability it declares; it cannot grant itself authority to do so.

```text
Authority
  M7
   │
   │ authorized ExecutionRequest
   ▼
M8 Capability Boundary
   │
   ├── operation → capability
   ├── capability → plugin
   │
   ▼
Concrete execution
```

## Existing-stack relationship

M8.2 does not replace `ToolDefinition`, `ToolRequest`, or `ToolResult`. It formalizes the higher-level mapping that was previously implicit in the tool layer.

`src/core/capability_catalog.py` remains the read-only discovery surface. `src/core/capability_invocation.py` remains the structural request builder. The new plugin boundary owns operation-to-capability-to-plugin resolution.

## Explicit non-goals

M8.2 does not implement:

- observation storage or context updates;
- retries, scheduling, or long-running execution;
- autonomous multi-step continuation;
- worker actors;
- natural-language capability selection;
- dynamic code loading or arbitrary plugin installation.

Those concerns belong to later M8 milestones or to controlled plugin infrastructure outside this boundary.

## Invariants

```text
operation binding is explicit
capability ownership is unique
plugin identity is unique
resolution is deterministic
resolution does not execute
plugin execution does not authorize
plugin result identity must match the selected capability
```
