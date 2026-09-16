# 374 — Role-Caller Dynamic Generation Guard

## Decision

Extend the role-caller generation surface audit so production callers cannot bypass explicit model-role routing by dynamically resolving `AIService.generate()` through `getattr()`.

## Boundary

`AIService.generate()` remains the provider-directed execution surface owned by `src/ai/service.py`. Production callers that require model-role selection must use `AIService.generate_for_role()` directly. Dynamic lookup of `generate` on `ai_service` / `_ai_service` is therefore treated as the same prohibited downgrade as a direct call.

The audit remains source-level and excludes test code plus `src/ai/service.py` itself. Provider implementations may continue to expose their own `generate()` methods.

## Rationale

M23.373 closed direct caller-level `generate()` and `generate_for_role()` compatibility-probing paths. A dynamic `getattr(ai_service, "generate")` path could still recreate the same silent downgrade without appearing as a direct attribute call. This guard closes that specific escape while preserving intentionally provider-directed generation inside `AIService`.

## Safety boundary

This change does not alter model selection, tool authority, permissions, execution, or verification semantics. It only turns an architectural caller constraint into another repository-level regression condition.

## Verification

User-local verification is required. The focused role-caller audit must pass with the new dynamic-generation check, followed by the existing core regression.
