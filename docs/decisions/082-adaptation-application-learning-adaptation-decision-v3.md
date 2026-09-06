# M23.84 — Application Learning Adaptation Decision v3

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`bcd0c0e9fe1c53cceaedc8390f18d2d4685dc196` — M23.83 implementation parent.

## Purpose
Establish the decision boundary immediately after M23.83 application-learning adaptation proposal v3.

A `PROPOSED` candidate becomes either `ACCEPTED` or `REJECTED` through an explicit decision input. A `BLOCKED` proposal remains `BLOCKED`. Decision evidence does not grant authorization or execute the proposed change.

## Contract
- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3` artifact.
- `PROPOSED` + `accept=True` → `ACCEPTED`.
- `PROPOSED` + `accept=False` → `REJECTED`.
- `BLOCKED` → `BLOCKED`, regardless of acceptance input.
- Preserves complete application provenance, state, evidence identities, confidence, fingerprints, authority/executor evidence, failure evidence, and lineage.
- Creates a new decision identity while preserving the proposal identity.
- Does not carry forward the proposal payload as executable authority.
- Recursively freezes decision basis, reasons, and lineage.
- Wrong source type or blank decision ID fails closed.
- No `execution_status` is introduced.

## Authority walls
Decision ≠ Authorization.
Decision ≠ Permission.
Decision ≠ Adaptation.
Decision ≠ Execution.
Decision ≠ Learning.
Decision ≠ Retry Permission.
Decision ≠ Scheduling.
Decision ≠ Model Update.
Decision ≠ Memory Mutation.
Decision ≠ Policy Mutation.
Decision ≠ Persistence Mutation.
Decision ≠ Truth.
Decision ≠ User Intent.

M23.84 is advisory-only. An `ACCEPTED` decision records bounded decision evidence; it does not itself authorize or execute adaptation.

## Rejection / blocking boundary
`REJECTED` and `BLOCKED` decisions remain inert evidence. They do not create execution authority or permit automatic corrective action.

## Atomicity
Target exactly **1 commit / 3 intended files** from M23.83.

## Local verification
Run:

```text
git fetch origin
git checkout feature/m23.84-world-model-rollback-repair-retry-adaptation-execution-learning-adaptation-application-learning-adaptation-decision-v3
git reset --hard origin/feature/m23.84-world-model-rollback-repair-retry-adaptation-execution-learning-adaptation-application-learning-adaptation-decision-v3

python -m unittest src.core.tests.test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3

python -m unittest discover -s src.core.tests -p "test_*.py"
```

Expected focused: **10/10**.
Expected core regression: **1345/1345**.

No merge unless explicitly requested.
