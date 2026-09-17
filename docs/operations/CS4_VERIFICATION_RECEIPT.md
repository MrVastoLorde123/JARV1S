# CS4 Verification Receipt

## Milestone

Deployment Closure CS4 — Durable Restart Proof

## Verified commit

- Branch: `feature/deployment-closure-cs4-durable-restart-proof`
- Head: `c4bcae1f1870afb2e77fd1fe5eb1f729d417c899`
- Base: `ea003e83c38699498a32e2c80db81e96ed4b02b0`
- Pull request: #425
- State: open / draft / unmerged

## Local verification

Focused restart proof:

```powershell
python -m unittest src.core.tests.test_deployment_closure_cs4_durable_restart -v
```

Result:

```
Ran 1 test in 0.048s
OK
```

CS3 learning compatibility gate:

```powershell
python -m unittest src.agents.tests.test_coding_execution_learning -v
```

Result:

```
Ran 4 tests in 0.110s
OK
```

Full regression:

```powershell
python -m unittest discover -s src.core.tests -p "test_*.py"
```

Result:

```
Ran 3294 tests in 5.403s

OK
```

The regression count is one higher than CS3's 3293 because CS4 adds one new restart-proof test.

## Scope verified

The CS4 production path now uses one explicitly composed `PersistentMemoryRepository` at:

`JARVIS_DATA_DIR / processed / jarvis.db`

That repository is injected into the shared `CodingExecutionLearningService` used by both the default processor and durable-session processor factory.

The focused restart test proves:

`completed execution evidence → candidate episodic memory → SQLite persistence → repository/service recreation → same memory and provenance recalled → repeat observation is idempotent`

CS4 does not promote candidate memory, establish truth/certainty, grant authority/authorization, or replay execution.

## Deployment-closure status

CS4 local verification is complete at `c4bcae1f1870afb2e77fd1fe5eb1f729d417c899`.

PR #425 remains intentionally open/draft/unmerged.
