# Runtime Model Catalog

The model catalog converts provider observations into explicit model-availability state for routing. It is observational only.

## Boundary

```text
provider /v1/models observation
        ↓
   ModelCatalog
        ↓
observed availability
        ↓
    ModelRouter
        ↓
 cognitive selection
```

The catalog does not:

- grant authority or permissions;
- expose tools;
- establish verification truth;
- claim a model is suitable merely because it is reachable;
- execute model requests.

A model can be observed as available while still being unsuitable for a role. Role fitness remains an explicit `ModelProfile` concern.

## OpenAI-compatible observation

`observe_openai_models()` accepts a provider-neutral `/v1/models`-style payload and observes the model IDs present in `data[].id`. Known profiles are marked available when observed and unavailable when absent from the latest observation.

Unknown observed IDs may be retained as observations for visibility, but they do not become routed profiles automatically.

## Next integration boundary

The next runtime integration may feed the catalog from the existing local provider health observation. That integration must preserve the separation between:

- model existence/availability;
- role fitness;
- routing selection;
- authority and permission;
- execution and verification.
