# 380–382 — Routing Runtime Synchronization and Observation Validation

## Decision

Close two runtime integrity gaps adjacent to the model-role contract.

### M23.380 — Live Policy Synchronization

`ModelRolePolicy` is mutable by explicit registration. `ModelRoutingRuntime` therefore synchronizes registered rules into its existing catalog before routing and projection operations. A newly registered model remains unroutable until it is both policy-profiled and observed.

### M23.381 — Immutable Role Sets

Model profiles and policy rules require `frozenset` role collections containing only explicit `ModelRole` values. Role fitness metadata cannot be mutated through an externally held mutable set.

### M23.382 — Observation Payload Validation

OpenAI-compatible model observations require a mapping payload and a sequence-valued `data` field before model IDs are extracted.

## Invariants

```text
Policy registration ≠ Model availability
Observation ≠ Role fitness
Role fitness ≠ Authority
Routing ≠ Authorization
Malformed observation ≠ Valid model state
Mutable caller data ≠ Immutable routing contract
```

These changes preserve the observation → policy → routing separation and do not grant execution rights, permissions, tools, confirmation, authorization, or verification truth.
