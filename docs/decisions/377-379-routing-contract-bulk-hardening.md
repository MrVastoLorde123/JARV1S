# 377–390 — Model Routing + AIService Contract Bulk Hardening

## Decision

Harden the model-routing and provider boundary as one coherent surface rather than allowing malformed role, observation, capability, or provider-response values to enter through adjacent constructors and execution paths.

### M23.377 — Profile / Decision Integrity

`ModelProfile` accepts only explicit `ModelRole` values and `RoutingDecision` requires a valid role, model identifier, reason, and candidate tuple.

### M23.378 — Policy Rule Integrity

`ModelRolePolicyRule` accepts only explicit `ModelRole` values so role fitness cannot be represented by arbitrary strings or other runtime values.

### M23.379 — Observation / Helper Integrity

`ModelObservation` requires a non-empty model identifier and `ModelCatalog.roles_for()` accepts only explicit `ModelRole` values.

### M23.380 — Live Policy Synchronization

`ModelRoutingRuntime` refreshes the policy-derived catalog when a new policy rule is registered. A newly registered model remains unroutable until provider observation marks it available.

### M23.381 — Immutable Role Sets

Profile and policy role declarations must be `frozenset` values containing only explicit `ModelRole` members.

### M23.382 — Observation Payload Validation

OpenAI-compatible `/v1/models` observation requires a mapping payload and a sequence-valued `data` field.

### M23.383 — Profile Registration Integrity

Identical profile registration is idempotent; conflicting replacement of a catalog profile is rejected deterministically.

### M23.384–386 — AIService Provider / Response Integrity

`AIService` requires registered providers to implement `AIProvider`, capability reporting to return `AICapabilities`, and provider generation to return `AIResponse`. Required capability names must be declared boolean fields. AI requests must contain a non-empty string task before provider execution.

### M23.387–389 — Provider Inventory / Provenance Integrity

Provider model inventories must contain only non-empty string model IDs. Provider responses must identify the provider actually used and include a non-empty model identifier.

### M23.390 — Test Contract Alignment

Legacy test doubles that participate in provider registration now implement the explicit `AIProvider` contract. Existing provider replacement behavior remains intact; production semantics are not weakened to accommodate stale fixtures. Unknown capability names are distinguished from known-but-unsupported capabilities.

## Invariants

```text
Observed model ID ≠ Model authority
Model role policy ≠ Permission
Model role ≠ Tool authority
Routing decision ≠ Execution authority
Model selection ≠ Authorization
Observation ≠ Trust
Capability name ≠ Capability support
Provider response ≠ Verification truth
Provider identity ≠ Model authority
```

These changes validate data and synchronization at explicit boundaries and do not grant authority, permissions, tools, execution rights, confirmation, verification truth, or user intent.

## Verification

User-local verification is intentionally batched across the AI and core suites:

```text
python -m unittest discover -s src.ai.tests -p "test_*.py"
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Both suites must pass before this bulk batch is treated as locally verified.
