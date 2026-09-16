# M35 — Authorized Execution Handoff

M35 establishes the narrow contract between bounded worker dispatch and the existing execution boundary.

## M35.1 Handoff Contract

An `ExecutionHandoff` pairs an M34 `DispatchResult` with an already-READY M7.10 `ExecutionPreparation`.

## M35.2 Identity Consistency

The handoff preserves step, worker, assignment, and execution identities and requires the execution request to match the dispatched step objective.

## M35.3 Authority Separation

M35 does not create authorization, policy, confirmation, execution preparation, provider selection, invocation, or execution.

## M35.4 Verification Gate

Focused contract tests and repository verification must pass before this milestone is considered locally verified.
