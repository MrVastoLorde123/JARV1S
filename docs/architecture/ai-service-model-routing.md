# AI Service Model-Routing Integration

The AI service is the execution bridge between JARVIS and provider implementations. Model routing sits immediately above provider execution as a cognitive-selection boundary.

## Contract

```text
request
  -> model-role routing
  -> selected model
  -> provider selection
  -> provider execution
  -> AI response
```

Model routing may select which model is appropriate for a role, but it does not grant authority, permissions, tools, execution rights, verification truth, or completion status.

## Required separation

- `ModelRouter` owns deterministic cognitive selection.
- `AIService` owns provider registration and provider execution.
- The control plane owns authority and permission.
- Tool authorization remains outside model selection.
- Verification remains an evidence-backed runtime concern.
- Model availability is an observation and may affect routing, but does not grant authorization.

## Explicit preference

A request may provide an explicit model preference. The router must validate that the preferred model serves the requested role and is available. A preference cannot cross role boundaries merely because the caller names a model.

## Current integration surface

`AIService.generate_for_role()` routes an `AIRequest` to a model role and then executes it through the selected provider. The selected model is copied into the provider-neutral request's `model` field. Existing `AIService.generate()` behavior remains available for provider-directed calls.

Role-routed generation is strict: `generate_for_role()` does not fall back to provider-default generation when routing is unconfigured. A caller requesting a cognitive role must therefore encounter a routing decision before provider execution. This keeps model-role callers on one deterministic contract and prevents a silent provider-default path from bypassing role policy.

This boundary intentionally does not yet:

- discover live `/v1/models` state;
- infer model fitness from provider connectivity;
- select based on resource or latency budgets;
- expose routing rationale as model chain-of-thought;
- grant tools or authority;
- change control-plane truth.

Those are subsequent boundaries.

## Acceptance criteria

- Role routing deterministically selects an available model.
- An explicit model preference is validated against the requested role.
- Routed execution reaches the selected provider with the selected model id.
- Unconfigured role-routed generation fails before provider execution rather than falling back to a provider default.
- Routing decisions contain no authority, permission, tool, execution, or verification fields.
- Legacy provider-directed `AIService.generate()` remains usable.
- Routing can be tested without an actual LLM or network connection.
