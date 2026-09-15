# Provider Model Observation in AIService

`AIService.observe_provider_models()` closes the provider-observation loop without turning model discovery into execution or authority.

```text
AI provider
   │ list_models()
   ▼
AIService.observe_provider_models()
   ▼
ModelRoutingRuntime
   ├─ ModelCatalog: observed availability
   ├─ ModelRolePolicy: explicit role fitness
   └─ ModelRouter: deterministic selection
```

The method invokes only a provider's explicit model-inventory surface. It does not call `generate()` and does not infer roles from discovered names.

A provider that does not expose model observation is rejected explicitly. An observed identifier without a matching role-policy rule remains visible but unroutable.
