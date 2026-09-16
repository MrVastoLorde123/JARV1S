# 377–379 — Model Routing Contract Bulk Hardening

## Decision

Harden the model-routing contract as one coherent boundary rather than allowing malformed role and observation values to enter through adjacent constructors.

### M23.377 — Profile / Decision Integrity

`ModelProfile` accepts only explicit `ModelRole` values and `RoutingDecision` requires a valid role, model identifier, reason, and candidate tuple.

### M23.378 — Policy Rule Integrity

`ModelRolePolicyRule` accepts only explicit `ModelRole` values so role fitness cannot be represented by arbitrary strings or other runtime values.

### M23.379 — Observation / Helper Integrity

`ModelObservation` requires a non-empty model identifier and `ModelCatalog.roles_for()` accepts only explicit `ModelRole` values.

## Invariants

```text
Observed model ID ≠ Model authority
Model role policy ≠ Permission
Model role ≠ Tool authority
Routing decision ≠ Execution authority
Model selection ≠ Authorization
Observation ≠ Trust
```

These changes validate data at the boundary and do not grant authority, permissions, tools, execution rights, confirmation, verification truth, or user intent.

## Verification

User-local verification is intentionally batched across the routing family:

```text
python -m unittest src.ai.tests.test_model_routing -v
python -m unittest src.ai.tests.test_model_role_policy -v
python -m unittest src.ai.tests.test_model_catalog -v
python -m unittest discover -s src.core.tests -p "test_*.py"
```

All focused routing-contract tests and the full core regression must pass before this batch is treated as locally verified.
