# M23.371 — Role Caller Routing Strictness

## Decision

Once a runtime caller has migrated to an explicit model role, it must require the role-routing surface provided by `AIService.generate_for_role()`.

A caller must not silently fall back to `AIService.generate()` when the role-routing method is unavailable.

## Rationale

M23.370 removed the temporary GENERAL fallback from `AIService.generate_for_role()`. Keeping caller-level downgrades would leave multiple hidden escape hatches where a supposedly role-routed cognitive request could still bypass deterministic model selection.

## Boundary

This milestone concerns cognitive selection only. Model routing does not grant authority, permissions, tools, execution rights, verification truth, or completion status.

Direct `AIService.generate()` remains valid for intentionally provider-directed calls outside role selection.

## Migrated callers

The strict role-routing surface is enforced by the current milestone for:

- coding planning (`CODING`)
- capability argument proposal (`GENERAL`)
- request intent classification (`GENERAL`)
- execution assessment interpretation (`GENERAL`)

The ordinary JARVIS conversation caller remains a follow-up core-orchestration boundary and is intentionally handled separately because its orchestration file is larger and spans additional runtime concerns.

## Verification

User-local focused and core regression verification remains required before completion.
