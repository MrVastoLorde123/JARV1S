# 373 — Role-Caller Generation Surface Audit

## Decision

Add a source-level regression guard for production AI callers so explicit cognitive-role callers cannot silently regress to provider-directed `AIService.generate()` or compatibility probing for `generate_for_role()`.

## Boundary

`AIService.generate()` remains the provider-directed execution surface owned by `src/ai/service.py`. Production cognitive callers outside that boundary must use `AIService.generate_for_role()` when model-role selection is required.

The audit intentionally excludes test doubles and the AIService implementation itself. It does not prohibit provider implementations from implementing their own `generate()` method.

## Rationale

M23.370–M23.372 removed the central and caller-level compatibility fallbacks. Without a repository-level guard, a future caller could reintroduce a silent downgrade while focused tests remain green.

The new audit turns that architectural rule into a durable regression condition.

## Verification

User-local verification is required. The new audit should run alongside the existing core regression and expose any remaining direct `_ai_service.generate()` / `ai_service.generate()` production caller or compatibility `getattr(..., "generate_for_role")` probe.
