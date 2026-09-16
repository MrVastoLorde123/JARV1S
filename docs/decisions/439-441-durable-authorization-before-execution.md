# M23.439–441: Durable Authorization Before Execution

## Boundary

Authorization evidence is recorded before a tool invocation is allowed to reach the execution adapter.

```text
Execution Plan
    |
    v
Concrete ToolRequest
    |
    v
Authorization Policy
    |
    v
ToolExecutionAuthorization
    |
    v
Durable ToolAuthorizationEvidence
    |
    v
Authorization Gate
    |
    v
Confirmation (when required)
    |
    v
ToolPlanStepHandler
    |
    v
Tool Invoker
```

## Invariants

- Planning does not authorize execution.
- Policy does not execute tools.
- Evidence persistence does not authorize requests.
- Evidence persistence does not report execution success.
- A denied authorization is recorded as denied evidence and never reaches the invoker.
- A persistence failure prevents execution.
- Required confirmation remains a separate gate after durable authorization.
- Verification of execution results remains a later boundary.

## Failure posture

The audited adapter fails closed when durable evidence cannot be written. This prevents an execution from occurring without a durable record of the authorization decision that preceded it.

## Scope

This boundary provides auditability and ordering. It is not a replacement for policy semantics, confirmation semantics, execution verification, or long-term evidence retention policy.
