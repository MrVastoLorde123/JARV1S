# JARVIS Testing & Quality Assurance Guide

## Overview

JARVIS strictly enforces deterministic testing across all subsystems before declaring features complete. 

Tests are organized into isolated test packages under `src/<subsystem>/tests/`.

---

## Test Directory Layout

```text
src/
├── ai/
│   └── tests/                 # AIService & Provider interface tests
├── context/
│   └── tests/
│       └── test_context_builder.py   # Context package construction & bounds
├── core/
│   └── tests/
│       ├── test_conversation.py      # Turn tracking, state snapshots & topics
│       └── test_jarvis.py            # End-to-end JARVIS orchestration
├── memory/
│   └── tests/
│       ├── test_evidence_store.py    # Provenance & evidence linking
│       ├── test_memory_formation.py  # Pipeline, candidate extraction & dedup
│       ├── test_memory_retrieval.py  # Text relevance & scoring engine
│       └── test_memory_store.py      # Database CRUD & validation
└── tests/
    └── test_database.py              # Schema integrity & connection tests
```

---

## Running Tests

### 1. Run Specific Subsystem Test Suites (Recommended)

Run the **Memory Formation & Retrieval** test suite:

```powershell
.venv\Scripts\python -m unittest discover -s src\memory\tests -v
```

Run the **JARVIS Core & Conversation State** test suite:

```powershell
.venv\Scripts\python -m unittest discover -s src\core\tests -v
```

Run the **Context Builder** test suite:

```powershell
.venv\Scripts\python -m unittest discover -s src\context\tests -v
```

### 2. Run Individual Test File

```powershell
.venv\Scripts\python -m unittest src.memory.tests.test_memory_formation -v
```

---

## Best Practices & Test Isolation Rules

1. **Temporary Database per Test**:
   Any test interacting with SQLite must use `tempfile.TemporaryDirectory()` and set `database.set_database_path()` in `setUp()`, cleaning up in `tearDown()`. Never touch `data/processed/jarvis.db` directly during test execution.

2. **No External AI API Calls in Unit Tests**:
   Unit tests must use `FakeAIProvider` (mock provider implementing `AIProvider`) rather than contacting real local or cloud servers.

3. **Deterministic Assertions**:
   Test assertions must verify exact values, exceptions (`with self.assertRaises(...)`), and structural bounds (turn limits, score orderings).

4. **Clean Module Imports**:
   Always import from the `src.` root package (e.g. `from src.memory.memory_store import add_memory`). Avoid modifying `sys.path` dynamically.
