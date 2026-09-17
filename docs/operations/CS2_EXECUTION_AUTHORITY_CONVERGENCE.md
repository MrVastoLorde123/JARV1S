# Deployment Closure CS2 — Execution Authority Convergence

## Scope

CS2 collapses the production execution-authority divergence identified during the deployment audit.

The canonical production path is now:

`plan → confirmation/policy → authorization → durable authorization evidence → integrity → sandbox admission → execution preparation → execution attempt → outcome`

The deterministic `ToolPlanStepHandler` remains an adapter. It does not become an authority boundary. The production invoker supplied to JARVIS is the existing `PolicyGate`, and the gate now records authorization evidence before execution.

## Authority rule

Execution is fail-closed when durable authorization evidence cannot be recorded.

A denied or confirmation-denied authorization is also recorded as evidence, but no execution attempt is admitted.

The separate `AuditedAuthorizedToolPlanStepHandler` remains available as an explicit reusable adapter for callers that need a core-level authorization policy contract. It is not a second production authority path in the local runtime.

## Production composition

`src/run_local_jarvis.py` now creates:

- `ToolAuthorizationEvidenceStore`
- `ToolAuthorizationEvidenceRecorder`
- `PolicyGate(..., authorization_recorder=...)`
- `ObservingToolInvoker(tool_stack.gate, ...)`
- `CodingAgentJARVIS(..., tool_invoker=coding_tool_invoker)`

This preserves the existing tool gate, sandbox, preparation, and execution-attempt boundaries while making durable authorization evidence part of the same authority path.

## Red-team coverage

Focused tests cover:

- missing/denied authorization → rejected
- authorization bound to the wrong step → rejected
- authorization bound to the wrong request → rejected
- denied authorization → rejected
- exact granted authorization → admitted
- durable-evidence failure → fail closed before execution
- policy denial → durable evidence + no handler execution
- valid authorization/admission → execution → concrete outcome

## Verification status

Implementation complete on branch `feature/deployment-closure-cs2-execution-authority-convergence`.

Required local gates before CS2 is closed:

```powershell
python -m unittest src.core.tests.test_deployment_closure_cs2_execution_authority -v
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Remote implementation is not considered local verification. The CS2 branch remains unmerged.
