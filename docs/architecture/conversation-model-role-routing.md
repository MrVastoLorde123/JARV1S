# Conversation Model-Role Routing

Ordinary JARVIS conversation is an explicit GENERAL cognitive-routing caller.

```text
user conversation
      |
      v
JARVIS._handle_conversation()
      |
      | generate_for_role(GENERAL)
      v
AIService
      |
      v
ModelRoutingRuntime
      |
      +-- observed availability
      +-- role policy
      +-- deterministic selection
      v
provider generation
```

The conversation caller must not silently substitute `AIService.generate()` when role routing is unavailable. A missing role-routing surface is a contract failure and must remain visible.

Provider-directed `AIService.generate()` calls remain valid elsewhere when the caller intentionally owns provider/model selection and does not require cognitive-role routing.

Selecting a GENERAL model does not grant authority, permissions, tools, execution rights, verification truth, or completion status.
