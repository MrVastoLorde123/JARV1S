# M23.372: JARVIS Conversation Routing Strictness

## Decision

`JARVIS._handle_conversation()` must use `AIService.generate_for_role(..., ModelRole.GENERAL)` directly. The conversation path must not probe for `generate_for_role()` and silently downgrade to provider-directed `generate()`.

## Rationale

M23.370 removed the temporary central GENERAL fallback from `AIService.generate_for_role()`. M23.371 removed equivalent caller-level fallbacks from the migrated cognitive planners and classifiers. Leaving the ordinary conversation path as a compatibility fallback would preserve a hidden escape hatch around the deterministic model-role boundary.

## Preserved boundary

`AIService.generate()` remains a valid provider-directed surface for callers that intentionally do not require role selection. This decision changes only the ordinary JARVIS conversation caller, which explicitly requires GENERAL cognitive selection.

Model-role selection remains advisory cognitive routing. It does not grant authority, permissions, tools, execution rights, verification truth, or user intent.

## Verification contract

The conversation routing test must prove GENERAL role selection, provider forwarding, and the absence of a legacy-generation fallback path.

User-local regression remains authoritative before the milestone is considered verified.
