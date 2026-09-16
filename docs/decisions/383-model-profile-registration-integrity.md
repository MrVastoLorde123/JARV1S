# 383 — Model Profile Registration Integrity

## Decision

`ModelCatalog.register_profile()` is now idempotent for the exact same immutable `ModelProfile` and rejects conflicting replacements for an existing `model_id`.

A model identifier represents one explicit role-fitness profile inside the runtime catalog. Silent replacement could otherwise mutate cognitive-selection semantics without a corresponding policy change or observation boundary.

## Invariants

```text
Same model ID + same profile → no-op / idempotent registration
Same model ID + different profile → deterministic rejection
Registration ≠ Observation
Registration ≠ Availability
Role fitness ≠ Authority
Routing ≠ Authorization
```

The change does not grant model authority, permissions, tools, execution rights, confirmation, or verification truth.
