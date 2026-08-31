# Filesystem Tool Cohesion

## Purpose

The workspace capability set currently consists of four filesystem-backed tools:

- `list_directory`
- `read_file`
- `search_files`
- `write_file`

They should behave as one coherent capability family while remaining independently implementable and discoverable through the normal tool infrastructure.

## Shared Boundary

All four handlers use `Workspace` for filesystem boundary behavior.

`Workspace` owns:

- one resolved base directory
- relative-path resolution
- rejection of absolute paths
- rejection of paths that resolve outside the workspace
- POSIX workspace-relative path reporting
- deterministic, bounded traversal
- hidden-entry filtering for traversal
- symlink handling and workspace confinement during traversal

Handlers do not reimplement those rules.

## Error Semantics

`ToolError` remains a generic result-level error model. The filesystem tools do **not** introduce a filesystem-specific error enum into the shared tool model.

The distinction is intentional:

### Shared semantic errors

The following codes are part of the shared workspace boundary and originate from `WorkspacePathError`:

```text
invalid_argument
path_outside_base_dir
```

Handlers translate these directly into failed `ToolResult` values.

### Capability-specific errors

Operations that have different semantics keep different error codes when that makes the result more precise.

Examples:

```text
read_file      -> file_not_found
list_directory -> directory_not_found
search_files   -> path_not_found
write_file     -> parent_not_found / file_exists
```

These should not be collapsed into a generic `not_found` code merely for superficial uniformity. JARVIS can therefore understand what operation failed without knowing the implementation of the handler.

## Limits

File-size and result-count limits remain handler-owned policies.

The fact that `read_file`, `search_files`, and `write_file` currently use a 1 MiB default does not make that number a workspace boundary. A future capability may legitimately require a different limit.

`search_files.max_results` is additionally bounded by the tool-level maximum, while `list_directory.max_entries` bounds directory enumeration. These are capability concerns, not workspace concerns.

## Result Shapes

Result payloads remain capability-specific because the operations answer different questions:

```text
list_directory -> entries
read_file      -> content
search_files   -> matches
write_file     -> write metadata
```

What is shared is the outer `ToolResult` contract, invocation correlation, structured errors, and workspace-relative path semantics.

## Composition Rule

JARVIS should compose the capabilities through the generic tool stack:

```text
ToolRequest
    |
    v
PolicyGate
    |
    v
ToolService
    |
    v
ToolHandler
    |
    v
ToolResult
```

JARVIS should not need to know:

- how a path is resolved
- how traversal is implemented
- whether a tool uses `os.walk` or another mechanism
- how a handler constructs its internal error
- how files are opened or scanned

The handler's published `ToolDefinition`, request schema, and result contract are the boundary.

## Why We Stop Here

It is tempting to extract every repeated string, default, and helper into a large filesystem abstraction. That would make the code look more unified while increasing coupling.

The current design extracts the behavior that is genuinely shared and leaves capability policy local.

> **Unify security boundaries and protocol semantics; keep capability intent and capability limits local.**

This is the cohesion boundary for the current filesystem milestone.
