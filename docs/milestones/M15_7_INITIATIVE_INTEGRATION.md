# M15.7 Initiative Integration

## Boundary

`InitiativeRuntime` is the immutable integration facade for the M15 proactive initiative pipeline.

It composes:

- opportunity/need detections
- initiative candidates
- evaluations
- proposals
- proactive schedules
- initiative safety results

## Invariants

- Integration ≠ Authorization
- Initiative ≠ Instruction
- Evaluation ≠ Permission
- Schedule ≠ Confirmation
- Safety Check ≠ Policy Decision
- Proactive Agency ≠ Unbounded Agency
- Proposal ≠ Execution

## Lineage

The runtime preserves explicit lineage:

`candidate → evaluation → proposal → schedule → safety`

M15 integration does not create a new authority path. Any action must still pass through the existing validation, policy, confirmation, authorization, and execution boundaries.
