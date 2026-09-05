# M22.50 — Preparation → Execution

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Boundary
M22.50 consumes exactly one M22.49 immutable future-execution preparation artifact and produces one immutable execution request, then invokes a replaceable applier through the execution service.

Execution is an attempt/observation boundary, not authorization. A preparation artifact cannot authorize execution merely by reaching M22.50; execution requests carry hard-false authority flags and the service does not mint authorization.

## Contract

Input:
- exactly one M22.49 preparation artifact;
- exact preparation identity and full known lineage;
- immutable payload/evidence/provenance;
- no authorization/start/retry/revocation/memory mutation/general authority flags.

Output:
- immutable execution request preserving exact M22.49 lineage;
- replaceable applier invocation;
- immutable `COMPLETED` or `FAILED` execution result;
- deterministic execution identity distinct from preparation and historical execution-source identities;
- non-authorizing result evidence.

Applier exceptions are normalized to `FAILED` with a non-empty reason. Successful calls produce `COMPLETED` with an observed result value.

## Authority wall

M22.50 cannot:
- grant authorization;
- request or mint authorization;
- mutate memory;
- request retry;
- request revocation;
- establish adaptation truth.

The execution result is an observation of an attempted application. Result integrity remains a separate downstream boundary.

## Identity and lineage

The execution request/result preserve the complete known M22.49 lineage:
`execution_id, preparation_id, admission_id, proposal_id, decision_id, evaluation_id, feedback_id, outcome_id, source_admission_id, source_proposal_id, decision_source_evaluation_id, evaluation_id_from_feedback, source_feedback_id, candidate_id, source_candidate_id, execution_source_id, source_execution_id, domain, source_policy_id, policy_id`.

`execution_id` is deterministic and distinct from the M22.49 preparation ID and the historical execution-source identity.

## Namespace integrity

M22.50 uses a dedicated `..._decision_proposal_admission_preparation_execution.py` namespace so the established M22.42 execution namespace remains unchanged.

## Verification

Focused suite:
`python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution -v`

Regression suite:
`python -m unittest discover -s src\\core -p "test*.py"`

Local verification is required before M22.50 can be marked VERIFIED / COMPLETE.

No merge performed.
