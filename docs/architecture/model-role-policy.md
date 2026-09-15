# Model Role Policy

The model role policy is the explicit fitness boundary between observed model identifiers and routable cognitive roles.

```text
provider /v1/models
        ↓
  ModelCatalog
        ↓ observed IDs
 ModelRolePolicy
        ↓ explicit role fitness
   ModelProfile
        ↓
   ModelRouter
        ↓
 cognitive selection
```

## Contract

`ModelRolePolicyRule` identifies one model ID and explicitly declares which JARVIS cognitive roles it may serve, plus deterministic routing priority and human-readable notes.

An observed model is **not** automatically assigned a role. A model only receives a routable profile when its exact identifier has a policy rule.

The policy does not:

- discover or prove model availability;
- execute model requests;
- grant tools, permissions, or authority;
- establish verification truth;
- infer role fitness from model size, reachability, or naming alone.

Availability remains owned by `ModelCatalog`. Role fitness remains owned by policy. Selection remains owned by `ModelRouter`.

## Snapshot behavior

`profiles_for_observed()` accepts observed IDs from the catalog and returns profiles only for IDs that have explicit policy rules. Unknown IDs remain visible to observation but are not routable.

This keeps empirical discovery separate from policy: discovering a new local model does not silently increase JARVIS's capabilities.

## Runtime direction

The next integration can load this policy from a runtime-owned configuration source and combine it with current catalog observations. The policy source should remain replaceable so model upgrades do not require changing routing semantics or authority boundaries.
