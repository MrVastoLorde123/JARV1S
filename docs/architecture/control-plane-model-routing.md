# Control-Plane Model Routing State

`control-plane.v1` now exposes the runtime-owned model-routing state as an observation surface.

## Projection

```text
local /v1/models observation
        |
        v
  ModelRoutingRuntime
   |       |       |
 Catalog  Role     Router
          Policy
        |
        v
 control-plane.v1 / model
```

The model projection contains:

- provider/model availability evidence;
- observed model identifiers;
- explicitly policy-profiled model roles and priorities;
- deterministic role selections and considered candidates;
- a read-only marker for the routing projection.

Unknown provider model identifiers remain visible but never receive a role merely because they were discovered.

## Authority boundary

The control-plane model projection does not grant:

- authority;
- permissions;
- tools;
- execution rights;
- verification truth.

A role selection is a cognitive-component selection only. Existing execution and authorization boundaries remain unchanged.

## Runtime bootstrap

The local runtime now constructs `ModelRoutingRuntime` from the explicit local model-role policy. The policy is configuration and should be treated as a replaceable local profile, not as benchmark truth.

Generation callers are not implicitly rewritten by this change. They can adopt `generate_for_role()` at explicit cognitive boundaries so migration remains observable and deterministic.
