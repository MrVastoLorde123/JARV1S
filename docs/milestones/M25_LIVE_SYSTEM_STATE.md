# M25 — Live System State

**Status:** implementation in progress.

M25 turns the already-existing runtime polling surface into an explicit, typed live-state contract. The cockpit observes runtime truth; it does not become an authority system or duplicate the control plane.

## Milestone chain

- **M25.1 — Runtime source:** preserve the existing control-plane, world-observation, and capability observation endpoints.
- **M25.2 — Typed live state:** normalize runtime payloads into `LiveSystemState`.
- **M25.3 — Freshness:** distinguish an observed timestamp from a fresh observation and fail closed when time data is absent or invalid.
- **M25.4 — Availability:** distinguish ready, degraded, unavailable, and unknown runtime conditions.
- **M25.5 — Safe normalization:** clamp progress, normalize optional values, and reject invalid state values from becoming UI truth.
- **M25.6 — Verification gate:** repository-local validation plus the UI build and established regression baseline.

## Boundary

M25 is observation. It does not grant authority, execute tools, or create a new durable runtime state store.

## Verification

Run:

```text
python scripts/verify_m25_live_system_state.py
```

Then:

```text
cd ui
npm run build
```

Finally rerun the established core/tools/AI regression baselines. M25 closes only after the user-local receipt is green.
