# 418–422 — Tool Execution Authorization Boundary

## Decision

Separate tool execution authorization from planning, capability realization,
confirmation, and low-level tool invocation.

### M23.418 — Authorization artifact

`ToolExecutionAuthorization` is an immutable decision bound to the exact
`PlanStep` and exact `ToolRequest`. It records whether execution is authorized,
which policy produced the decision, and the policy's reason.

### M23.419 — Policy contract

`ToolAuthorizationPolicy` is an injected authority-bearing boundary. The
policy is outside planning and capability realization. The execution layer
accepts its decision but does not invent or reinterpret policy.

### M23.420 — Deterministic request identity

`ToolPlanStepHandler.build_request()` exposes one canonical deterministic
materialization of the request represented by a `USE_TOOL` plan step. The
authorization boundary and the execution boundary therefore operate on the
same request identity.

### M23.421–422 — Authorized execution composition

`AuthorizedToolPlanStepHandler` requires a policy decision before delegating to
the existing policy-neutral `ToolPlanStepHandler`. Missing, denied, or
mis-bound authorization stops execution before the invoker is reached.

Confirmation remains independent:

```text
Plan ≠ Authorization
Plan ≠ Confirmation
Authorization ≠ Confirmation
Authorization ≠ Verification truth
Authorization + required Confirmation → execution may proceed
Denied/Stale/Missing Authorization → no invocation
```

The low-level `ToolService` remains unaware of policy and confirmation.
Capability realization remains proposal/request preparation only.

## Verification

User-local verification is intentionally batched:

```text
python -m unittest src.core.tests.test_authorized_tool_execution -v
python -m unittest src.core.tests.test_tool_execution -v
python -m unittest discover -s src.core.tests -p "test_*.py"
python -m unittest discover -s src.tools.tests -p "test_*.py"
```
