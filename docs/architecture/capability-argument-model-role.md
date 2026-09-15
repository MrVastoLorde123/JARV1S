# Capability Argument Model Role

The capability argument planner uses the explicit `GENERAL` model role to translate natural-language intent into proposed structured arguments.

```text
selected capability + user intent
            ↓
AIRequestArgumentPlanner
            ↓
AIService.generate_for_role(GENERAL)
            ↓
JSON argument proposal
            ↓
CapabilityInvocationBuilder
            ↓
validated ToolRequest
```

The model proposes data only. It does not select arbitrary tools, grant authorization, invoke capabilities, or establish verification truth.

`CapabilityInvocationBuilder` remains the deterministic validation/materialization boundary, and the later tool authorization and execution layers remain unchanged.

Legacy AIService-like behavior remains available through the existing compatibility fallback when a test double exposes only `generate()`.
