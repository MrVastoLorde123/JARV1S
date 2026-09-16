# 416–417 — Tool Execution Confirmation Gate

## Decision

Close the execution-boundary gap where a `PlanStep` could declare
`requires_confirmation=True` while the tool plan handler ignored that field
and invoked the tool directly.

### M23.416 — Explicit Confirmation Artifact

Introduce `ToolExecutionConfirmation` as a frozen, request-bound artifact.
It identifies the exact plan step and exact `ToolRequest`, and carries an
explicit boolean confirmation state.

### M23.417 — Confirmation Enforcement

`ToolPlanStepHandler` constructs the deterministic `ToolRequest` first and,
when the plan step requires confirmation, refuses execution unless the
provided confirmation is:

- a `ToolExecutionConfirmation`;
- confirmed;
- bound to the exact step ID; and
- bound to the exact request, including tool, arguments, and invocation ID.

A missing, stale, rejected, or malformed confirmation cannot reach the tool
invoker.

## Boundary invariants

```text
Plan intent ≠ confirmation
Confirmation ≠ permission
Confirmation ≠ authorization
Confirmation ≠ verification truth
PlanStep.requires_confirmation=True → explicit confirmation required
Confirmation for another request → rejected
Rejected confirmation → no tool invocation
```

The low-level `ToolService` remains unaware of confirmation and continues to
own only tool request/result structural integrity. Higher-level policy and
authority remain separate concerns.

## Verification

User-local verification is intentionally batched:

```text
python -m unittest src.core.tests.test_tool_execution -v
python -m unittest discover -s src.core.tests -p "test_*.py"
python -m unittest discover -s src.tools.tests -p "test_*.py"
```
