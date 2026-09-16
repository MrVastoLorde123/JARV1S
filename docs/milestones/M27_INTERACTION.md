# M27 — Interaction

**Status:** VERIFIED / COMPLETE.

M27 turns the existing explicit chat/command surface into a durable typed interaction contract. The user remains the source of intent; the interface submits exactly what the user explicitly sends and reports the transport outcome without collapsing observation into authority.

## Milestone chain

- **M27.1 — Interaction contract:** define request, response, error, and lifecycle state types.
- **M27.2 — Explicit submission:** preserve the existing `/api/command` path and user-triggered submit boundary.
- **M27.3 — Session/request identity:** retain request and session identifiers across the interaction boundary.
- **M27.4 — Response/error normalization:** reject empty or malformed response identity/content safely.
- **M27.5 — Authority separation:** keep interaction state separate from authorization, execution, verification, and capability discovery.
- **M27.6 — Verification gate:** repository-local validation plus UI build and established regression baseline.

## Boundary

M27 is interaction and transport presentation. It introduces no new authority, no automatic execution, and no second command or durable state system.

## Verification

Verified from the user-local receipt on the `feature/m27-interaction` head:

```text
M27 interaction contract: PASS
UI production build: PASS
Core regression: 3276/3276 OK
```

M27 is closed. The verified head becomes the baseline for M28.
