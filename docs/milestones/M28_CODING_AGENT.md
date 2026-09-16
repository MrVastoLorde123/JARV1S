# M28 — Coding Agent

**Status:** implementation in progress.

M28 establishes coding as a first-class JARVIS agent role while preserving the existing deterministic authority chain. The repository already contains a bounded coding planner/worker, explicit confirmation service, plan fingerprinting, tool-gated file edits, and constrained verification. M28 adds the durable typed lifecycle contract around that existing machinery.

## Milestone chain

- **M28.1 — Coding-agent boundary:** document the separation between coding intelligence and execution authority.
- **M28.2 — Lifecycle contract:** define understanding, planning, confirmation, execution, verification, completion, blocked, and failed states.
- **M28.3 — Safe state model:** validate task identity, edit bounds, operation identity, and terminal lifecycle states.
- **M28.4 — Existing worker alignment:** retain exact-plan execution and the constrained `write_file` / `run_test` surface.
- **M28.5 — Verification gate:** run focused coding-agent tests, existing coding-worker tests, UI build, and the established core regression baseline.

## Boundary

M28 is coding-agent orchestration and state visibility. It does not replace JARVIS authority, add an arbitrary command executor, or bypass confirmation, authorization, execution, or verification.

## Verification

```text
python -m unittest src.agents.tests.test_coding_agent_contract -v
python -m unittest src.agents.tests.test_coding_worker -v
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

M28 closes only after the user-local receipt is green.
