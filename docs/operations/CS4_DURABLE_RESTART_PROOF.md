# CS4 — Durable Restart Proof

## Boundary

CS4 proves that the learning state written by CS3 remains available after the persistence repository is recreated, and that the deployed runtime binds that repository to the configured `JARVIS_DATA_DIR`.

`execution → observed outcome → candidate episodic learning → SQLite persistence → repository recreation → durable recall`

CS4 does not:
- promote candidate memory to active state;
- establish truth or certainty;
- grant authority or authorization;
- replay or repeat the completed execution.

## Runtime composition

The local composition root now constructs one `PersistentMemoryRepository` from:

`JARVIS_DATA_DIR / processed / jarvis.db`

and injects one `CodingExecutionLearningService` built from that repository into both the default and durable session processor paths.

This removes the previous implicit default path inside `CodingExecutionLearningService()` from the production deployment path.

## Restart proof

The focused CS4 test:
- writes a verified coding-learning record to a temporary SQLite database;
- destroys the first repository/service objects;
- creates a fresh repository/service over the same database file;
- recalls the same memory and provenance;
- records the same execution again and verifies idempotency rather than creating a duplicate.

## Verification gate

Run:

```powershell
python -m unittest src.core.tests.test_deployment_closure_cs4_durable_restart -v
python -m unittest src.agents.tests.test_coding_execution_learning -v
python -m unittest discover -s src.core.tests -p "test_*.py"
```

The full regression remains authoritative.
