# Model Catalog to Routing Bridge

The runtime model catalog is the observation source for deterministic model routing when live model availability is known.

```text
provider observation
       ↓
ModelCatalog
       ↓
observed ModelProfiles
       ↓
ModelRouter
       ↓
role selection
       ↓
AIService provider execution
```

A refresh replaces the routing availability view; it does not mutate role fitness, authority, permission, tool inventory, or verification state.

## Guarantees

- A known model absent from the latest observation cannot remain routable through stale availability state.
- A known model observed by the provider can become routable only if its declared role profile permits the requested role.
- Routing remains deterministic for a given catalog snapshot.
- Catalog refresh does not execute a provider request.
- The provider execution path remains behind `AIService.generate()` / `generate_for_role()`.

## Non-guarantees

Model presence does not prove quality, safety, authority, or successful execution. Those remain separate runtime concerns.
