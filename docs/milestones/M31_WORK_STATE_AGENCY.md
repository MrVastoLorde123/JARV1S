# M31 — Work State / Agency Substrate

**Status:** implementation in progress.

M31 establishes Work State as the operational substrate for the V6 agency layer. It describes current work and dynamically selects the descriptive operational role appropriate to that work without creating permanent role-agents or moving authority out of the established control boundaries.

## Milestone chain

- **M31.1 — Work-state contract:** define immutable work identity, objective, lifecycle, progress, blockers, evidence cursor, required capabilities, and assigned agents.
- **M31.2 — Dynamic roles:** infer researcher, requirements analyst, technical lead, debugger, reviewer, release coordinator, or general role from observable work-state signals.
- **M31.3 — Separation:** keep Work State distinct from Memory, Evidence, Authority, and Permissions.
- **M31.4 — Agency substrate:** make the contract usable by future task/planning/agent orchestration without creating a second authority system.
- **M31.5 — Verification gate:** focused work-state tests plus UI build and established core regression.

## Boundary

M31 is operational state and orchestration context. It does not authorize actions, execute tools, persist memory, or create permanent specialized agents.

## Verification

```text
python -m unittest src.agency.tests.test_work_state -v
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

M31 closes only after the user-local receipt is green.
