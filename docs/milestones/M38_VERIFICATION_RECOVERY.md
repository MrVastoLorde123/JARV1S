# M38 — Verification Recovery

## Purpose

Connect independently verified agency outcomes to bounded objective completion or continuation without creating an execution path.

## Deliverables

- immutable `RecoveryDecision`
- explicit complete/continue/blocked/uncertain/rejected dispositions
- reuse of existing M9.7 `DriveabilityController`
- no authorization or execution surface
- focused recovery tests
- repository-local contract gate

## Boundary

M38 decides what bounded recovery state follows verification. It does not verify the world, authorize an action, execute an action, or manufacture evidence.
