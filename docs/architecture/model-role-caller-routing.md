# Model-Role Caller Routing

AI-backed runtime callers that require cognitive model selection must use the explicit `AIService.generate_for_role()` surface.

```text
AI caller
   |
   | generate_for_role(role)
   v
AIService
   |
   v
ModelRoutingRuntime
   |
   +-- observed availability
   +-- explicit role policy
   +-- deterministic selection
   v
provider generation
```

A migrated role caller must not silently downgrade to `AIService.generate()` when role routing is unavailable. Such a downgrade bypasses the deterministic cognitive-selection boundary.

`AIService.generate()` remains valid for intentionally provider-directed calls that do not require role selection.

Role selection does not grant authority, permissions, tools, execution rights, verification truth, or completion status.
