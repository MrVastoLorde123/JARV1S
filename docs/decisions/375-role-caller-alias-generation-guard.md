# 375 — Role-Caller Alias Generation Guard

## Decision

Extend the production role-caller source audit so provider-directed `AIService.generate()` cannot be reintroduced through local aliases of `ai_service` / `_ai_service`.

## Boundary

The audit tracks simple direct and transitive local-name aliases whose value originates from the recognized AIService receiver attributes. Calls through those aliases are treated as equivalent provider-directed generation and are rejected outside `src/ai/service.py`.

The rule remains source-level only. It does not change runtime generation, model routing, authority, permissions, tool access, execution, or verification semantics.

## Rationale

Direct-call and dynamic-lookup guards can be bypassed by assigning an AIService reference to another local name before calling `generate()`. The alias-aware audit closes that static regression path while avoiding a broad ban on unrelated `generate()` methods.

## Verification

User-local verification is required. The focused role-caller audit should pass before the existing core regression is rerun.