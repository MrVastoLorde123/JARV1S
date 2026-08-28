# Command System

## Purpose

The JARVIS command system provides an explicit and structured interface for user-directed operations.

Commands are intentionally separated from ordinary conversation.

Normal conversation is interpreted by the conversational and AI layers. Commands are parsed, validated, routed, and executed through dedicated command infrastructure.

The command system therefore provides a controlled path between explicit user intent and system operations.

## Architecture

```text
Raw Input
    |
    v
CommandParser
    |
    v
CommandRequest
    |
    v
CommandService
    |
    v
CommandRegistry
    |
    v
CommandHandler
    |
    v
CommandResult
```

Each layer has one responsibility.

### CommandParser

Determines whether input is an explicit command.

Examples:

```text
/SHOW-MEMORY pcvue_skill
/REMEMBER I prefer local AI
/CONFIRM
```

Normal conversational input is not converted into a command.

The parser also normalizes command names and supports quoted arguments.

Example:

```text
/REMEMBER "local AI is preferred"
```

becomes:

```python
CommandRequest(
    name="REMEMBER",
    arguments=("local AI is preferred",)
)
```

### CommandRequest

`CommandRequest` is the provider-neutral representation of an explicit command.

It contains:

* command name
* arguments
* original raw input
* optional metadata

The model does not execute anything.

### CommandRegistry

The registry maps command names to implementations.

Example:

```text
SHOW-MEMORY -> ShowMemoryHandler
REMEMBER    -> RememberMemoryHandler
CONFIRM     -> ConfirmCommandHandler
CANCEL      -> CancelCommandHandler
```

Handlers are plugins.

The registry therefore allows new command capabilities to be added without modifying the command service itself.

### CommandService

The service orchestrates command execution.

It:

1. receives parsed or raw command input
2. resolves the appropriate handler
3. executes the handler
4. validates the returned `CommandResult`
5. coordinates confirmation staging when required

The service does not implement command-specific behavior.

## Handler Boundary

Every command is implemented through a `CommandHandler`.

```python
class CommandHandler(ABC):
    def command_name(self) -> str:
        ...

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:
        ...
```

This creates a plugin boundary.

Future commands can therefore be introduced without turning `jarvis.py` or `service.py` into a collection of command-specific conditionals.

## Current Commands

### `/SHOW-MEMORY`

Read-only memory inspection.

```text
/SHOW-MEMORY pcvue_skill
```

The handler:

1. attempts an exact memory-key lookup
2. falls back to semantic retrieval
3. returns the best matching memory
4. includes important metadata and evidence count

It does not mutate memory.

### `/REMEMBER`

Explicit user-directed memory creation.

```text
/REMEMBER I prefer local AI
```

The handler constructs a `CandidateMemory` and sends it through the existing memory decision architecture.

It does not write directly to SQLite.

The effective architecture is:

```text
/REMEMBER
    |
    v
CandidateMemory
    |
    v
MemoryDecisionService
    |
    v
MemoryDecision
    |
    v
MemoryDecisionExecutor
    |
    v
Memory Store
```

This ensures explicit memory creation and automatic memory formation share the same mutation boundary.

## Why Commands Are Separate From Conversation

A command is explicit user intent.

A normal conversational statement is not necessarily an instruction.

For example:

```text
"I'm learning PCVUE."
```

may produce a memory candidate through automatic formation.

But:

```text
/REMEMBER I'm learning PCVUE.
```

is an explicit instruction to create memory.

This distinction allows JARVIS to assign different trust and authorization rules to different forms of input.

## Design Principles

### Commands are explicit

A command must use the explicit command syntax.

### Commands are structured

The command subsystem works with typed models rather than raw strings after parsing.

### Commands are modular

Each command is a handler plugin.

### Commands do not bypass subsystem boundaries

A memory command uses the memory subsystem.

A future filesystem command should use the filesystem/tool subsystem.

A future system command should use the system/tool subsystem.

### Commands should remain small

A command should have one clear responsibility.

Broad functionality should be exposed through multiple commands rather than one universal command handler.

## Future Direction

The command system is intentionally designed to expand.

Potential future commands include:

```text
/SEARCH-MEMORY
/ARCHIVE
/RESTORE
/DELETE
/HELP
/STATUS
```

Higher-risk capabilities may eventually include:

```text
/EXEC
/WRITE-FILE
/MODIFY-CODE
```

These must use stricter authorization and confirmation mechanisms.

## Security Direction

The command system is not intended to become an unrestricted execution layer.

The long-term model is:

```text
Command
    |
    v
Policy
    |
    v
Permission
    |
    v
Confirmation
    |
    v
Execution
```

This becomes especially important once JARVIS has access to tools, files, operating-system operations, or code modification.

## Architectural Rule

> A command is the explicit, validated path from user intent to a system operation.

Commands must not become shortcuts around JARVIS's safety architecture.
