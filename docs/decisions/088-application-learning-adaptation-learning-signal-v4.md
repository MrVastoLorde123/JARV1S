# M23.90 — Application Learning Adaptation Learning Signal v4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`fdb487dd2dd24dea4addbc253d085d4b42f23c49` — M23.89 VERIFIED / COMPLETE.

## Purpose
M23.90 establishes the bounded learning-signal boundary immediately after M23.89 evaluation. It converts one evaluated observational outcome-feedback artifact into one immutable learning signal without turning that signal into learning, model update, retry authorization, execution authority, scheduling, or mutation.

## Contract
- Consumes exactly one M23.89 application outcome feedback evaluation v3 artifact.
- Produces exactly one immutable M23.90 learning-signal artifact with a new `signal_id`.
- Preserves evaluation, feedback, classification, integrity, application, decision, proposal, and outcome identities.
- Preserves confidence, selected fingerprints, failure evidence, evaluation status, and lineage.
- Signal status is explicit: `POSITIVE_SIGNAL`, `NEGATIVE_SIGNAL`, `REJECTION_SIGNAL`, `AMBIGUOUS_SIGNAL`, or `NON_INFORMATIVE_SIGNAL`.
- `INFORMATIVE` evaluation maps from outcome identity to positive, negative, or rejection signal.
- `AMBIGUOUS` evaluation produces `AMBIGUOUS_SIGNAL`.
- `NON_INFORMATIVE` evaluation produces `NON_INFORMATIVE_SIGNAL`.
- Failure feedback requires failure evidence.
- Non-failure feedback cannot carry failure evidence.
- Recursively freezes reasons and lineage.
- Wrong source type, blank signal ID, invalid status combination, or missing failure evidence fails closed.

## Authority walls
Learning Signal ≠ Learning.
Learning Signal ≠ Truth.
Learning Signal ≠ Retry Authorization.
Learning Signal ≠ Authorization.
Learning Signal ≠ Scheduling.
Learning Signal ≠ Execution.
Learning Signal ≠ Model Update.
Learning Signal ≠ Memory Mutation.
Learning Signal ≠ Policy Mutation.
Learning Signal ≠ Persistence Mutation.
Learning Signal ≠ User Intent.

The artifact is intentionally advisory and observational. It represents evidence suitable for later learning logic; it does not perform the learning operation.

## Verification
Pending local receipt.

Focused:
```text
python -m unittest src.core.tests.test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_v4
```

Expected focused: **14/14**.

Core regression baseline: **1414 tests** after M23.89; expected **1428/1428** after M23.90.

```text
python -m unittest discover -s src.core.tests -p "test_*.py"
```

## Atomicity
Exactly **1 commit / 3 intended files** from M23.89.

No merge unless explicitly requested.
