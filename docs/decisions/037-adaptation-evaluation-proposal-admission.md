# Decision 037 — Adaptation Evaluation Proposal → Admission Boundary

## Decision

An `LearningWriteAdaptationEvaluationProposal` must cross a separate deterministic admission boundary before any future execution or mutation path.

## Rationale

A proposal expresses an intended downstream change; admission evaluates whether that proposal satisfies explicit structural requirements. Keeping admission separate prevents proposal creation from becoming implicit authorization or execution.

## Contract

- Input is an exact immutable `LearningWriteAdaptationEvaluationProposal`.
- Output is an immutable `LearningWriteAdaptationEvaluationProposalAdmission`.
- Admission status is explicitly `ADMITTED` or `REJECTED`.
- Proposal, decision, evaluation, feedback, source-feedback, candidate, source-candidate, execution, admission-lineage, and domain identities are preserved exactly.
- Proposal payload, evidence, provenance, and confidence are validated.
- Confidence remains bounded to `[0.0, 1.0]`; deterministic baseline admits confidence >= 0.5.
- Admission identifiers are deterministic for identical source proposal evidence.
- Provider output is identity-validated.
- Admission is evidence of policy evaluation only; it does not authorize execution, retry, revocation, or memory mutation.

## Authority walls

- Proposal ≠ Admission
- Admission ≠ Authorization
- Admission ≠ Execution
- Admission ≠ Retry Authorization
- Admission ≠ Revocation
- Admission ≠ Memory Mutation
- Evaluation ≠ Truth
- Evidence ≠ Truth
- Learning ≠ Authority
