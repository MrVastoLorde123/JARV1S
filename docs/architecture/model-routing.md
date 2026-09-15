# JARVIS Model Routing Contract

Model selection is a cognitive-routing decision, not an authority decision.

The router may choose a model for a role such as `GENERAL`, `CODING`, `DIAGNOSTIC`, `VERIFICATION`, or `LIGHTWEIGHT`. It may consider observed availability, explicit user preference, and deterministic role priority.

The router must not grant or imply:

- authority;
- repository permissions;
- tool permissions;
- execution rights;
- verification truth;
- task completion;
- user intent.

## Contract

```text
request
  -> role requirement
  -> observed model candidates
  -> deterministic selection
  -> routing decision
  -> existing AI/provider execution boundary
```

A routing decision identifies **which cognitive component should be used**. It does not execute the model and does not expand the capabilities available to it.

## Empirical roster guidance

The current local evidence suggests differentiated roles are more useful than a single universal model:

- Granite 8B: general/verification-oriented local default candidate;
- Qwen3 14B: diagnostic/troubleshooting specialist candidate;
- SAGE 14B: structured diagnostic specialist candidate;
- Hermes 4 14B: general engineering specialist candidate;
- Granite 30B: expensive deep-reasoning candidate;
- Qwen3-Coder 30B: expensive coding candidate;
- lightweight 4B-class models: fast specialist candidates.

These are roster observations, not authority rules. Actual runtime availability and deployment configuration remain authoritative.

## Next boundary

This contract intentionally stops before provider execution. The next integration boundary may connect `ModelRouter` to `AIService`, then expose the resulting runtime-selected model as an observation in the control plane. Neither integration should allow a model selection to mutate authority or tool permissions.
