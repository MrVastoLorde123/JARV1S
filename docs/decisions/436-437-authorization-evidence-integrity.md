# M23.436–437 — Authorization Evidence Integrity

## Decision

Persisted authorization evidence is content-addressed by a deterministic SHA-256 identity derived from its canonical JSON-native record.

A read operation must reconstruct the immutable `ToolAuthorizationEvidence` value and recompute the identity from that reconstructed value. If the stored identifier does not match the reconstructed evidence, the store raises an integrity-validation error instead of returning the altered record.

## Boundary

```text
Authorization Policy
        │
        ▼
ToolExecutionAuthorization
        │
        ▼
ToolAuthorizationEvidence
        │
        ▼
Evidence Store ── integrity validation ──► durable evidence
```

The evidence store does not:

- authorize a request;
- execute a tool;
- satisfy confirmation requirements;
- assert that execution succeeded;
- repair or overwrite tampered evidence automatically.

## Why

Authorization evidence is intended to explain why a concrete tool request was permitted or denied. A database record that can be altered while retaining its original identifier must not be silently treated as the original decision.

The integrity check therefore converts the persistence layer from a passive key/value store into a deterministic evidence boundary without giving it authority over execution.

## Verification

The focused persistence tests cover:

- stable identity and round-trip reads;
- idempotent writes;
- distinct evidence identities;
- scoped deterministic reads;
- invalid input rejection;
- JSON independence from `ToolResult`;
- tamper detection through `get()`;
- tamper detection through `all()`;
- tamper detection through `list_for_step()`.
