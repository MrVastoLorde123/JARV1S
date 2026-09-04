# M16.3 — Controlled Modification Planning

## Objective

Define a bounded planning object that translates a self-development proposal and its change-impact assessment into an ordered, testable, recoverable modification plan.

## Boundary

A `ControlledModificationPlan` is descriptive planning state. It is not execution, authorization, approval, confirmation, policy, or instruction.

The plan preserves lineage to both the M16.1 proposal and M16.2 impact assessment.

## Model

`SelfDevelopmentProposal`
→ `ChangeImpactAssessment`
→ `ControlledModificationPlan`

The plan contains ordered `ModificationStep` records plus validation gates, rollback checkpoints, constraints, and immutable metadata.

## Step kinds

- INSPECT
- PREPARE
- MODIFY
- TEST
- OBSERVE
- VERIFY
- CHECKPOINT
- ROLLBACK

These describe planned work only. A step of kind `MODIFY` does not perform a modification.

## Safety walls

- Plan ≠ Execution
- Plan ≠ Authorization
- Plan ≠ Approval
- Plan ≠ Policy
- Step ≠ Execution
- Validation Gate ≠ Authorization
- Rollback Checkpoint ≠ Rollback Execution
- Authority Review ≠ Authority Grant
- Self-Development ≠ Authority Expansion

## Required properties

- Immutable and bounded data.
- At least one typed step.
- Unique step identifiers, validation gates, rollback checkpoints, and constraints.
- Explicit lineage through proposal and assessment IDs.
- Authority-review information may be carried forward but can never grant authority.
- Serialization explicitly records that authorization and execution were not granted or requested.
