# Confirmation System

## Purpose

The confirmation system provides a reusable safety boundary for operations that require explicit approval before execution.

The core principle is:

> **Confirmation authorizes an already-defined operation; it does not create a new interpretation of the user's request.**

This distinction prevents a confirmation request from being reinterpreted after the user has approved it.

## Architecture

```text
Potentially Dangerous Operation
              |
              v
       CommandService
              |
              v
      PendingOperation
              |
              v
     Explicit User Approval
              |
          /CONFIRM
              |
              v
       Confirmed Operation
              |
              v
          Execution
```

Cancellation follows the same model:

```text
PendingOperation
      |
   /CANCEL
      |
      v
CANCELLED
```

## PendingOperation

A `PendingOperation` is a concrete operation waiting for explicit approval.

It contains:

* operation ID
* command
* arguments
* human-readable description
* creation timestamp
* status
* metadata

Example:

```python
PendingOperation(
    operation_id="...",
    command="DELETE",
    arguments=("pcvue_skill",),
    description="Delete memory pcvue_skill.",
    status="PENDING",
)
```

The operation is therefore defined before confirmation occurs.

## Lifecycle

A pending operation follows this lifecycle:

```text
PENDING
   |
   +----> CONFIRMED
   |
   +----> CANCELLED
```

Terminal states cannot be confirmed again.

This prevents accidental repeated authorization.

## `/CONFIRM`

The `/CONFIRM` command confirms the currently pending operation.

It does not itself execute arbitrary operations.

Instead:

```text
/CONFIRM
    |
    v
PendingOperation
    |
    v
CONFIRMED
```

Execution remains a separate concern.

This allows the command system to distinguish:

```text
authorization
```

from:

```text
execution
```

## `/CANCEL`

The `/CANCEL` command removes authorization from the pending operation by transitioning it to `CANCELLED`.

Example:

```text
/DELETE pcvue_skill

JARVIS:
This operation will delete memory pcvue_skill.
Confirmation required.

/CANCEL
```

The operation is then no longer executable through the normal confirmation path.

## Current Scope

V1 keeps pending operations in memory.

This is intentional.

Confirmation state is:

* temporary
* operational
* separate from memory
* separate from conversation history

Persistent confirmation state can be introduced later if the application requires it.

## Why Confirmation Is Separate

Confirmation is not a property of one command.

It is a reusable safety mechanism.

Future commands may require confirmation:

```text
/DELETE
/RESET
/EXEC
/MODIFY-CODE
```

Therefore confirmation belongs to the command infrastructure rather than being hard-coded into individual commands.

## Authorization vs Interpretation

The distinction is fundamental.

Incorrect design:

```text
/DELETE pcvue_skill
      |
      v
pending approval
      |
      v
/CONFIRM
      |
      v
reinterpret latest user request
```

Correct design:

```text
/DELETE pcvue_skill
      |
      v
PendingOperation(
    command="DELETE",
    arguments=("pcvue_skill",)
)
      |
      v
/CONFIRM
      |
      v
authorize that exact operation
```

The operation being confirmed must already exist.

## Safety Principle

Confirmation should protect against accidental execution without silently altering the requested operation.

Approval means:

> Execute the operation I was shown.

It does not mean:

> Re-evaluate what I may have meant.

## Future Authorization Model

The current confirmation system is intentionally small.

A future architecture may include:

```text
Command
   |
   v
Risk Classification
   |
   v
Permission Check
   |
   v
Confirmation Policy
   |
   v
PendingOperation
   |
   v
Explicit Approval
   |
   v
Execution
```

This will allow low-risk commands to execute immediately while high-risk operations require stronger protection.

Potential risk levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## Future Self-Modification Safety

The confirmation mechanism becomes particularly important when JARVIS gains the ability to modify files or code.

A future workflow may look like:

```text
JARVIS identifies improvement
        |
        v
Creates proposal
        |
        v
Shows intended changes
        |
        v
Requests approval
        |
        v
Confirmed operation
        |
        v
Tool execution
        |
        v
Tests
        |
        v
Review
```

This allows JARVIS to become increasingly capable without making every capability implicitly trusted.

## Architectural Rule

> Authorization is a state transition on a specific pending operation.

It must never become a second interpretation of user intent.
