# Decision 016 — Execution Preparation / Handoff Boundary

## Status

Accepted for M22.11.

## Decision

JARVIS must cross an explicit, non-executing execution-preparation boundary after sandbox admission and before tool execution.

`ExecutionPreparationService.prepare()` consumes the exact `ToolRequest`, granted `AuthorizationDecision`, valid `AuthorizationIntegrityResult`, and admissible `SandboxAdmissionDecision`. It produces an immutable `ExecutionHandoff` that preserves the upstream identities needed to prove what was authorized and what sandbox was admitted.

`PolicyGate.invoke()` must require successful preparation immediately before delegating to `ToolService`.

## Authority walls

- Sandbox Admission ≠ Execution Preparation
- Execution Preparation ≠ Execution
- Execution Preparation ≠ Worker Assignment
- Execution Preparation ≠ Process Launch
- Execution Preparation ≠ Containment Activation
- Upstream authorization evidence ≠ fresh authorization
- Preparation ≠ permission escalation

## Required properties

1. Handoff is immutable and inspectable.
2. The handoff is bound to the exact authorization identity.
3. The handoff preserves request and authorization-integrity fingerprints.
4. The handoff preserves the admitted sandbox profile identity.
5. Tool and invocation identities must match across request, authorization, and admission evidence.
6. Failed preparation cannot reach `ToolService`.
7. Preparation grants no new authority and starts no execution activity.

## Explicit non-goals

M22.11 does not assign workers, activate sandbox containment, spawn processes, execute plugins, persist authorization, add revocation or expiration, or create a second invocation path outside `PolicyGate`.
