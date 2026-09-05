# M22.47 — Future Adaptation Execution Feedback Result Integrity Feedback Evaluation Decision → Proposal

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Boundary
M22.47 consumes exactly one M22.46 decision artifact and converts only an `ACCEPT` decision into an immutable downstream proposal. `DEFER` and `REJECT` produce no proposal.

## Contract
Input:
- exactly one M22.46 decision;
- exact decision/evaluation/feedback/execution lineage;
- bounded confidence and provider metadata.

Output:
- deterministic proposal identity;
- explicit accepted-evaluation proposal kind;
- exact preservation of known M22.46 lineage;
- recursively immutable payload, evidence, provenance, and metadata;
- bounded confidence.

## Authority wall
The proposal cannot authorize or execute anything. It cannot request retry, revocation, memory mutation, or general authority, and it cannot establish adaptation truth. Downstream admission remains independent.

## Identity
The proposal ID is deterministic and distinct from decision, evaluation, feedback, and execution identities. The M22.46 decision's existing `proposal_id` is preserved separately as `source_proposal_id`.

## Namespace integrity
M22.47 uses `learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal.py`, leaving the historical M22.37 module unchanged.

## Verification
Focused suite:
`python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal -v`

Regression suite:
`python -m unittest discover -s src\\core -p "test*.py"`
