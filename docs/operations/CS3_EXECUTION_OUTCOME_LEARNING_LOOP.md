# Deployment Closure CS3: Execution → Outcome → Learning Loop

## Purpose

CS3 closes the production runtime gap between an already-completed coding execution and durable learning evidence.

The existing coding worker remains the sole executor for the coding operation. CS3 observes its returned `CodingAgentResult`; it never executes the tool plan a second time.

## Runtime boundary

```text
confirmed coding plan
        ↓
canonical tool-gated CodingAgentWorker execution
        ↓
CodingAgentResult
        ↓
CodingClaimEvidenceAdapter (M29)
        ↓
Experience + OutcomeAssessment + Evaluation
        ↓
PersistentMemoryRepository
        ↓
EPISODIC / CANDIDATE learning record
```

The durable record is deliberately `CANDIDATE`, not `ACTIVE`. Persistence therefore records experience for later learning/consolidation without silently promoting a model, changing policy, or granting authority.

## Invariants

CS3 does not authorize execution, does not invoke tools, does not request retries, does not establish truth or certainty, and does not promote persistent memory to active state.

A learning-persistence failure is reported in the execution response metadata but cannot retroactively change or repeat the completed execution.

The learning identity is deterministic from the observed claim/evidence set, so repeating the same observed result is idempotent at the durable-memory boundary.

## Production integration

`CodingAgentJARVIS._confirm_coding()` continues to call the existing `CodingAgentService.execute()` exactly once. After the returned result, it invokes `CodingExecutionLearningService.record(...)` and exposes the learning receipt in response metadata.

## Verification target

Focused tests:

```text
python -m unittest src.agents.tests.test_coding_execution_learning -v
```

Full regression:

```text
python -m unittest discover -s src.core.tests -p "test_*.py"
```

The authoritative local verification receipt will be recorded after the user reruns these commands on the CS3 branch.
