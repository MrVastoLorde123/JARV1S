# Decision 055 — M9.5 Delegation / Coordination

## Status

Accepted — M9.5 implementation in progress.

## Decision

M9.5 introduces a bounded delegation coordinator that validates worker assignments against the registered workforce and produces a deterministic assignment order.

The coordinator is an orchestration layer, not an authority layer. It may decide which already-bounded worker assignment is next within an explicit plan, but it cannot authorize actions, create execution requests, grant capabilities, or execute workers directly.

## Core invariants

```text
Delegation ≠ Authorization
Coordination ≠ Authority
Worker A ≠ Authority over Worker B
Sequencing ≠ Escalation
Worker Output ≠ Permission
```

## Execution rule

Every executable worker action still requires its own M7 `ExecutionPreparation` and remains subject to M8 execution semantics.

## Determinism and bounds

- Assignment identities are unique within a delegation plan.
- Plans have a hard maximum assignment count.
- Dependencies are explicit and cannot reference unknown assignments or themselves.
- Dependency cycles are rejected.
- Worker bounds are revalidated through `WorkerRegistry` before coordination succeeds.
- No hidden coordination loop or implicit worker capability acquisition is permitted.
