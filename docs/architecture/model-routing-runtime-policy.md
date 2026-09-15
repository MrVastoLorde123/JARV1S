# Model Routing Runtime Policy Bridge

`ModelRoutingRuntime` is the deterministic runtime boundary that combines three separate concerns without collapsing them:

```text
provider observation
       ↓
 ModelCatalog  ← existence / availability
       ↓
ModelRolePolicy ← explicit role fitness
       ↓
 ModelRouter   ← cognitive selection
       ↓
 AIService
```

## Responsibilities

`ModelRoutingRuntime` owns the lifecycle needed to refresh routing from current observations. It initializes routable profiles from explicit policy rules, applies the latest provider observation to availability, rebuilds routing state, and exposes routing decisions to `AIService`.

An observed identifier that has no policy rule remains visible in the catalog but produces no routable profile. This prevents model discovery from silently increasing JARVIS capabilities.

## Authority boundary

The runtime bridge does not grant:

- tools;
- permissions;
- authority;
- execution rights;
- verification truth.

`AIService.generate_for_role()` still performs provider execution only after deterministic routing has selected the cognitive model. The provider remains the execution mechanism; the routing layer never becomes an execution authority.

## Snapshot semantics

Each provider observation is treated as the latest availability snapshot. A model absent from that snapshot becomes unavailable for routing. Unknown model IDs can be retained as observed identifiers while remaining unroutable without explicit policy.
