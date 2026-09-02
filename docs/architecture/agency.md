# JARVIS Agency Architecture

## Boundary

Agency begins where M7 ends.

M7 produces a provider-neutral `ExecutionRequest` only after the deterministic authority chain has completed successfully. M8 owns everything downstream of that handoff.

```text
M7
Authority
   ↓
ExecutionRequest
   ↓
M8
Agency Runtime
```

## M8 Responsibility

The agency runtime should be responsible for turning an authorized request into a controlled operation and recording what happened.

```text
ExecutionRequest
      ↓
Capability / Plugin Selection
      ↓
Invocation Boundary
      ↓
Execution
      ↓
Observation
      ↓
Result / Error
      ↓
Verification
      ↓
State / Context Update
```

## Important Separation

M8 must not quietly move authority into the executor.

The executor receives an already-authorized handoff. It does not re-authorize the action, rewrite provenance, or grant itself additional permissions.

Likewise, an execution failure must remain observable. A failed action is not converted into success by an AI interpretation.

## Plugin Boundary

JARVIS's long-term plugin architecture should fit inside this agency layer:

```text
JARVIS
   ↓
Authority
   ↓
Agency Runtime
   ↓
Plugin / Capability
   ↓
External System
```

Plugins provide capabilities. They do not become the source of JARVIS authority.

## Worker Boundary

The future workforce is an extension of agency rather than a replacement for it.

```text
Agency Runtime
      ↓
Worker Assignment
      ↓
Worker Execution
      ↓
Observed Outcome
```

Workers should be bounded by capabilities, inputs, outputs, and execution policy. A worker is an actor inside JARVIS's agency system, not an unrestricted second authority system.
