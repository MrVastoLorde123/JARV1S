# Decision 056 — M9.6 Workforce Reliability / Recovery

## Status

Accepted — M9.6 implementation in progress.

## Decision

M9.6 extends M8.6 reliability semantics across delegated worker assignments without creating a second authority system.

Recovery may classify outcomes, preserve provenance, determine bounded retry eligibility, and produce recovery intent. It may not authorize, execute, broaden capability, acquire credentials, skip delegation dependencies, or silently restart work.

## Core invariants

```text
Recovery ≠ Authorization
Retry Eligibility ≠ Permission
Failure Handling ≠ Authority Escalation
Worker Recovery State ≠ Global Authority
Resumption ≠ Re-Authorization
Recovery Sequencing ≠ Dependency Bypass
```

## Boundaries

Recovery state preserves `plan_id`, `assignment_id`, `worker_id`, execution/result identity where available, explicit state, attempt count, and evidence. Retry intent is bounded and requires fresh M7 authorization for any follow-up execution. Dependency order remains explicit and cannot be bypassed. Identical recovery evidence is idempotent; conflicting evidence remains an explicit conflict.

M9.6 must not mutate authorization, grant capability, expand scope, acquire credentials, execute workers, invoke plugins directly, transfer authority, expand global context access, or create unbounded retry/recovery loops.

M8.6 remains the execution-level reliability boundary; M9.6 adds worker identity, assignment scope, delegation continuity, and report provenance to that reliability model.
