# 376 — Model-Role Request Type Boundary

## Decision

Require `RoutingRequest.role` to be an explicit `ModelRole` value at construction time.

## Boundary

Model routing consumes explicit cognitive-role identifiers. A caller must not silently substitute an arbitrary string or other value and rely on downstream routing behavior to interpret it.

This is a contract-validation boundary only. It does not grant authority, permissions, tools, execution rights, or verification truth.

## Rationale

The routing stack is intentionally role-driven and deterministic. Failing at the request boundary keeps malformed role requests from reaching selection logic, where errors could otherwise depend on incidental enum/string behavior or fail later while formatting diagnostics.

## Verification

User-local verification is required. Run the focused model-routing contract tests followed by the full core regression.
