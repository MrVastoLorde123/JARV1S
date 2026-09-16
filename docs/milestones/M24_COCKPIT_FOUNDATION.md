# M24 — Cockpit Foundation

**Status:** implementation complete; awaiting user verification receipt.

M24 establishes the first durable visual contract for JARVIS's operational cockpit. The interface is a presentation surface over runtime-owned state; it does not become a second authority system.

## Milestone chain

- **M24.1 — Surface:** establish the cockpit entry and preserve the existing React/Vite application shell.
- **M24.2 — Runtime identity:** make the cockpit explicitly represent JARVIS as an operating environment rather than a generic chat page.
- **M24.3 — Operational state contract:** define a typed cockpit snapshot with work state, health, activity, and explicit authority fields.
- **M24.4 — Verification gate:** add a repository-local contract check for the cockpit surface and M24 state model.
- **M24.5 — Authority visualization:** retain the invariant that connectivity, capability availability, model state, planning, and UI state do not imply authorization.
- **M24.6 — Work visibility:** expose active work, lifecycle, blockers, agents, verification, and activity through the existing control-oriented UI surfaces.
- **M24.7 — Responsive cockpit:** preserve usability across desktop and narrow layouts through the existing functional and space-specific UI layers.

## Bulk boundary

M24 is intentionally bulked around **visibility**, not around backend execution. Where existing runtime/control-plane surfaces already provide the needed information, M24 consumes those surfaces rather than creating duplicate authority or state stores.

No new execution authority is introduced by M24.

## Verification

Run:

```text
python scripts/verify_m24_cockpit.py
```

Then run the UI build:

```text
cd ui
npm run build
```

Finally, run the established core/tools/AI regression baselines from the M23 V1 closure receipt.

M24 closes only when all requested gates are green.
