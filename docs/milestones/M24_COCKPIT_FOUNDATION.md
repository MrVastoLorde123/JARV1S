# M24 — Cockpit Foundation

**Status:** VERIFIED / COMPLETE.

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

## Verification receipt

Verified on the user's local workspace from remote head `a2d63752a51628de77abb03a92701f98c815868d`:

```text
python scripts/verify_m24_cockpit.py
M24 cockpit contract: PASS

python -m unittest discover -s src.core.tests -p "test_*.py"
Ran 3276 tests in 6.789s
OK

cd ui
npm run build
vite v8.3.0 building client environment for production...
✓ 17 modules transformed.
✓ built in 193ms
```

The remote M24 branch is 9 commits ahead and 0 behind the verified M23 baseline, and PR #377 remains draft/open/unmerged by design.

M24 is **VERIFIED / COMPLETE**. M25 may begin from this verified head.
