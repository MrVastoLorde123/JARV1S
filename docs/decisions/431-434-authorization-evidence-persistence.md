# M23.431–434 — Authorization Evidence Persistence Boundary

## Decision

Authorization decisions produce immutable evidence that may be persisted by a dedicated evidence store. Persistence is downstream of authorization and does not become part of the execution authority path.

```text
Concrete ToolRequest
        │
        ▼
Policy Evaluation
        │
        ▼
ToolExecutionAuthorization
        │
        ▼
ToolAuthorizationEvidence
        │
        ▼
Evidence Store
```

The evidence store is deliberately separate from `ToolPlanStepHandler`, `ToolService`, confirmation, and execution-result handling.

## Invariants

- Evidence is bound to the exact step/request decision through the immutable evidence snapshot.
- Evidence identity is deterministic from the serialized evidence fields.
- Re-saving identical evidence is idempotent.
- Distinct authorization decisions receive distinct evidence identities.
- Missing or malformed evidence identifiers are rejected.
- Persistence does not authorize a request.
- Persistence does not confirm user intent.
- Persistence does not execute a tool.
- Persistence does not claim that execution succeeded.
- Evidence remains distinguishable from `ToolResult` execution outcomes.

## Storage boundary

`ToolAuthorizationEvidenceStore` owns only the authorization-evidence table and uses its own connection lifecycle. It can operate against the normal JARVIS SQLite database or an isolated database path for tests/deployment contexts.

The store is intentionally not wired into execution in this milestone. Composition may persist a decision before or after the execution boundary, but persistence itself has no authority to advance execution.

## Identity

Evidence identity is the SHA-256 digest of the canonical JSON representation of `ToolAuthorizationEvidence.to_record()`. This makes identical decisions idempotent without introducing a mutable counter or execution-side sequence.
