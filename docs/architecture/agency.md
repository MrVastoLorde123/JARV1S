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

The agency runtime is responsible for turning authorized requests into controlled operations and recording what happened.

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

## M8.5 Controlled Multi-Step Agency

M8.5 adds bounded orchestration without moving authority into the agency layer.

```text
M7-authorized Preparation #1
        ↓
M8.4 Lifecycle
        ↓
M8.1 Runtime
        ↓
Observation #1
        ↓
Updated WorkingContext
        ↓
M7-authorized Preparation #2
        ↓
M8.4 Lifecycle
        ↓
M8.1 Runtime
        ↓
Observation #2
        ↓
...
```

The coordinator owns sequencing, context progression, observation accumulation, identity uniqueness, and a hard step limit. It never creates authorization, selects policy, directly invokes plugins, or treats one observation as permission for the next action.

Every distinct action must therefore re-enter through the established M7 authority chain before execution.

## Important Separation

M8 must not quietly move authority into the executor or orchestrator.

The executor receives an already-authorized handoff. It does not re-authorize the action, rewrite provenance, or grant itself additional permissions.

Likewise, an execution failure must remain observable. A failed action is not converted into success by an AI interpretation or hidden retry loop.

## Plugin Boundary

JARVIS's long-term plugin architecture fits inside this agency layer:

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
