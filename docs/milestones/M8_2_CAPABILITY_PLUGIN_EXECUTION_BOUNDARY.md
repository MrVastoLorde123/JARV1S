# M8.2 — Capability / Plugin Execution Boundary

**Status:** VERIFIED

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
           ↓
   M8.1 ExecutionOutcome
```

## Responsibilities

- give plugins a stable identity and version;
- let a plugin expose one or more declared `ToolDefinition` capabilities;
- prevent duplicate plugin identities;
- prevent multiple plugins from owning the same capability name;
- bind provider-neutral M8 operations explicitly to declared capabilities;
- resolve an operation deterministically without executing anything;
- validate capability arguments before plugin execution;
- execute a resolved capability through its owning plugin;
- preserve `execution_id` as the invocation identity;
- reject plugin results that claim to belong to a different capability;
- translate concrete plugin results into the provider-neutral M8.1 `ExecutionOutcome` contract.

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

A plugin receives a `ToolRequest` derived from an already-authorized `ExecutionRequest` through the explicit M8 execution boundary. The plugin can perform the capability it declares; it cannot grant itself authority to do so.

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
   │
   ▼
M8.1 ExecutionOutcome
```

## Existing-stack relationship

M8.2 does not replace `ToolDefinition`, `ToolRequest`, or `ToolResult`. It formalizes the higher-level mapping that was previously implicit in the tool layer.

`src/core/capability_catalog.py` remains the read-only discovery surface. `src/core/capability_invocation.py` remains the structural request builder. The plugin boundary owns operation-to-capability-to-plugin resolution and adapts concrete results to the M8.1 runtime contract.

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
arguments are validated before plugin execution
plugin execution does not authorize
plugin result identity must match the selected capability
M8.2 adapts results; M8.1 owns execution lifecycle semantics
```

## Verification

Focused command:

```bash
python -m unittest src.core.tests.test_plugin_boundary -v
```

Result: **12/12 tests passed.**

Full repository verification was run from the user's real checkout using the repository `unittest` suite.

Result: **904/904 tests passed.**

No GitHub Actions run is being treated as verification; the authoritative evidence for this milestone is the successful local test execution above.
