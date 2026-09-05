# Decision 045 — M22.40 Future Adaptation Execution Feedback Proposal Admission

## Status

Proposed implementation boundary.

## Boundary

`Future Adaptation Execution Feedback Proposal → Future Adaptation Execution Feedback Proposal Admission`

## Context

M22.39 creates an immutable, inert future-adaptation execution feedback proposal from an accepted M22.38 decision. The next boundary must screen that proposal before any downstream execution-preparation stage.

## Contract

M22.40 consumes exactly one `LearningWriteAdaptationEvaluationExecutionFeedbackProposal`.

Admission must:

- validate the exact M22.39 proposal type;
- validate required proposal lineage and identity;
- validate proposal payload, evidence, provenance, and bounded confidence;
- produce explicit `ADMITTED` or `REJECTED` admission status;
- preserve the complete known proposal lineage, including decision identity, M22.37 evaluation identity, historical evaluation identity, feedback/source-feedback, candidate/source-candidate, execution/source-execution, preparation, source admission, source proposal identity, domain, and source policy identity;
- assign a distinct deterministic admission identity;
- preserve recursively immutable proposal/evidence/provenance snapshots;
- apply a deterministic baseline admission policy;
- expose a provider-neutral admission interface whose output identity is checked against the exact proposal context.

The deterministic baseline admits confidence `>= 0.5` when proposal payload, evidence, and provenance are non-empty. Otherwise it rejects.

The admission policy identity is distinct from the proposal's source policy identity so later policy evolution does not overwrite lineage.

## Authority wall

Admission is not execution authorization.

The M22.40 admission result cannot:

- authorize execution;
- request execution;
- request retry;
- revoke execution;
- mutate memory;
- grant general authority.

Downstream execution preparation remains a separate boundary.

## Rationale

A proposal describes a possible future adaptation. Admission determines whether that proposal satisfies the structural and policy requirements for the next stage. Keeping admission deterministic and separate prevents proposal-generation logic from silently becoming permission.

Preserving both `source_admission_id` and the new `admission_id` keeps the lineage of the original future-execution path while making the new screening event independently auditable.

## Verification

Focused:

`python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_execution_feedback_proposal_admission -v`

Regression:

`python -m unittest discover -s src\\core -p "test*.py"`

## No merge

M22.40 remains independently implemented and must receive a local test receipt before being marked GREEN / VERIFIED / COMPLETE.
