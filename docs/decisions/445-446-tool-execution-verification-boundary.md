# M23.445–446: Tool Execution Verification Boundary

## Decision

A successful tool invocation is an execution outcome, not proof that the intended effect occurred.

JARVIS therefore introduces an explicit `ToolExecutionVerifier` boundary that evaluates a concrete
`ToolRequest` and its `ToolResult` and returns an immutable `ToolExecutionVerification`.

## Invariants

- Authorization answers whether execution is permitted.
- Confirmation answers whether an independently required confirmation artifact exists.
- Execution produces a `ToolResult` reported by the tool boundary.
- Verification independently evaluates whether the intended effect is established.
- `ToolResult.success=True` never implies `VERIFIED`.
- `VERIFIED`, `FAILED`, and `UNVERIFIED` are explicit states.
- Verification is bound to the exact request/result tool and invocation identity.
- Verification has no execution, authorization, or confirmation authority.

## Boundary

```text
Plan
  |
  v
Authorization --> durable authorization evidence
  |
  v
Confirmation (when required)
  |
  v
Execution --> ToolResult
  |
  v
Verification --> VERIFIED / FAILED / UNVERIFIED
```

A verifier may use an independent observation, a second read, a device state query, a checksum,
or another domain-specific signal. The verifier owns the interpretation of that evidence; the
execution adapter does not infer success from the original tool response.

## Non-goals

This milestone does not define a universal verification strategy for every tool and does not
persist verification evidence yet. Those are separate boundaries.
