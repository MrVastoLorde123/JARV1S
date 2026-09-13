# Decision 038 — Interface Shell Stabilization and Space Contract

## Status

Proposed implementation boundary for the first post-M52 interface repair.

## Decision

Promote the UI from the M28 minimal truth shell into a stable application shell with four explicit operational spaces:

```text
CHAT          intent / conversation
CONTROL       consequence / execution / authority state
MIND          world/context/relationship state
CAPABILITIES  available backend capabilities
```

The spaces are presentation boundaries. They do not grant authority, reinterpret backend truth, or execute actions by themselves.

## Contract

- The UI must render a visible shell even when every backend endpoint is unavailable.
- Backend failures are displayed as state, not allowed to blank the application.
- World, command, and capability data remain separate concerns.
- The UI must preserve explicit authority signals supplied by the backend and never infer authority from connectivity, capability presence, or command success text.
- Command submission is an explicit user action.
- No automatic command execution is introduced by the interface shell.
- The interface may observe backend state; it does not become an authority layer.

## White-screen protection

The entry point must contain a top-level React error boundary. A rendering exception must produce a visible recovery surface instead of a blank document.

## Verification

Required local gates:

- `npm run build` from `ui`
- rendered shell with all backend services unavailable
- rendered shell with world/capability services available
- explicit command submission path
- responsive layout at desktop and mobile widths
