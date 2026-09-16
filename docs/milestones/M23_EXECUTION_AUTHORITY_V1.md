# M23 — Execution Authority V1 Closure

**Status: VERIFIED / COMPLETE**

**Verification baseline:** commit `182bd31` on `feature/m23.377-379-routing-contract-bulk-hardening`.

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
      ↓
Recovery Recommendation
      ↓
Correction / Review / Completion
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

### Recovery

Recovery consumes verification evidence only to recommend a bounded next control stage. `COMPLETE`, `CORRECT`, and `REVIEW` are recommendations, not permission, execution, retry, or policy mutation.

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

## Closed-loop evidence path

```text
Authorization Evidence
        +
Execution Observation
        +
Verification Evidence
        ↓
Inert Learning Signal
        ↓
Recovery Recommendation
```

The learning and recovery stages consume evidence; they do not gain execution authority from it.

## Final V1 verification receipt

Local verification was completed after M23.468:

- Focused verification-evidence store: **10/10 OK**
- Core regression: **3276/3276 OK**
- Tools regression: **892/892 OK**
- AI regression: **111/111 OK**
- Execution chain: **5/5 OK**
- Chain adapter: **4/4 OK**
- Learning signal: **3/3 OK**
- Recovery boundary: **4/4 OK**

The previous Windows SQLite cleanup failure was corrected in M23.468 by making test-side SQLite connections follow an explicit commit/rollback/close lifecycle. The production verification evidence store already uses deterministic connection closure.

Implementation completion is distinct from local verification; with the receipts above, this document is now treated as **VERIFIED / COMPLETE**.
