# Local Provider Model Observation

`LocalProvider.list_models()` is the provider-specific observation seam for an OpenAI-compatible local `/v1/models` endpoint.

It reports model identifiers exposed by the local server. It does not:

- execute a generation request;
- select a model role;
- grant authority or permissions;
- grant tools;
- establish model quality or fitness;
- claim that the selected model is safe or verified.

The observation can feed `ModelCatalog`, which in turn feeds deterministic `ModelRouter` availability.

```text
local /v1/models
      ↓
LocalProvider.list_models()
      ↓
ModelCatalog.observe_ids()
      ↓
ModelRouter
```

Generation remains a separate operation through `AIService.generate()` or `AIService.generate_for_role()`.
