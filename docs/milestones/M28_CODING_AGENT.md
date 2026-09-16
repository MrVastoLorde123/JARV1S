# M28 — Coding Agent

**Status:** VERIFIED / COMPLETE.

M28 establishes coding as a first-class JARVIS agent role while preserving the existing deterministic authority chain. The repository already contains a bounded coding planner/worker, explicit confirmation service, plan fingerprinting, tool-gated file edits, and constrained verification. M28 adds the durable typed lifecycle contract around that existing machinery.

## Verified chain

- **M28.1 — Coding-agent boundary:** complete.
- **M28.2 — Lifecycle contract:** complete.
- **M28.3 — Safe state model:** complete, including optional metadata defaulting safely to an empty mapping.
- **M28.4 — Existing worker alignment:** complete; exact-plan execution and constrained `write_file` / `run_test` surface preserved.
- **M28.5 — Verification gate:** complete.

## Boundary

M28 is coding-agent orchestration and state visibility. It does not replace JARVIS authority, add an arbitrary command executor, or bypass confirmation, authorization, execution, or verification.

## Verification receipt

User-local verification passed:

```text
python -m unittest src.agents.tests.test_coding_agent_contract -v
Ran 3 tests — OK

python -m unittest src.agents.tests.test_coding_worker -v
Ran 6 tests — OK

cd ui
npm run build
Build completed successfully.

python -m unittest discover -s src.core.tests -p "test_*.py"
Ran 3276 tests — OK
```

M28 is closed at commit `7f8043f5764e45ee44ae45c556138440e91024c0`.
