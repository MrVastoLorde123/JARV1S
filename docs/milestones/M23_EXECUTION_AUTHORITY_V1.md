# M23 — Execution Authority V1 Closure

## V1 acceptance contract

The execution path is considered implemented when the repository can represent and compose these boundaries without collapsing them:

```text
User / Environment
      ↓
Request / Task
      ↓
Plan
      ↓
Validation
      ↓
Policy
      ↓
Confirmation (when required)
      ↓
Concrete ToolRequest
      ↓
Authorization Decision
      ↓
Durable Authorization Evidence
      ↓
Execution
      ↓
Raw ToolResult Observation
      ↓
Independent Verification
      ↓
Durable Verification Evidence
      ↓
Inert Learning Signal
```

## Invariants

### Authorization

Authorization is immutable, bound to the exact plan step and concrete request, and persisted before invocation. Missing, denied, stale, or mismatched authorization prevents invocation.

### Confirmation

Confirmation remains a separate execution precondition. Authorization does not imply confirmation and confirmation does not create authorization.

### Execution

The low-level executor is policy-neutral. A raw execution result remains an observation even when it reports success.

### Verification

Verification is injected and independent. `ToolResult.success=True` is not sufficient to establish verified effect. Verification can explicitly produce `VERIFIED`, `FAILED`, or `UNVERIFIED`.

### Durability

Authorization and verification evidence are separately persisted, content-addressed, idempotent, and tamper-detecting. Persistence failures fail closed before execution or evidence acceptance respectively.

### Learning

Execution evidence may be converted into an inert learning signal. The signal records authorization, execution, verification status, and lineage, but cannot execute, authorize, retry, mutate memory/policy, or establish truth by itself.

## Existing runtime composition

The completed chain is exposed through `ToolExecutionChain` and can be bound to the existing `PlanExecutor` `USE_TOOL` action via `ToolExecutionChainPlanHandler`. The existing `PolicyGate` remains available below that composition boundary for tool-layer policy, confirmation, integrity, sandbox, and handoff enforcement.

```text
PlanExecutor
    ↓ USE_TOOL
ToolExecutionChainPlanHandler
    ↓
ToolExecutionChain
    ├── Authorization Policy
    ├── Authorization Evidence Store
    ├── Confirmation Precondition
    ├── ToolInvoker
    ├── Verification Service
    └── Verification Evidence Store
```

## Final V1 verification requirement

Implementation completion is distinct from local verification. The repository must pass the final focused and regression suites before this document is treated as `VERIFIED / COMPLETE`.
