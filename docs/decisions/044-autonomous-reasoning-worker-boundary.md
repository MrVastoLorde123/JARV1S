# Decision 044 — Autonomous Reasoning Worker Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce an injected `AutonomousReasoningWorker` that performs one provider-backed reasoning cycle for an `AutonomousJob` and converts the provider response into the existing autonomous cycle contract.

The worker:

- builds a provider-neutral `AIRequest` from the job goal and working context;
- calls the existing `AIService`;
- parses the returned content as an `AutonomousReasoningAction`;
- converts that action into one `AutonomousCycleResult`;
- preserves the reasoning action in the cycle context when a tool request is pending;
- never invokes a tool, grants authorization, mutates persistence, or selects provider-specific execution behavior.

## Tool boundary

`TOOL_REQUEST` is represented as `WAIT_TOOL` until a later runtime boundary interprets and executes the request through the existing `ToolService`. This deliberately prevents the model-facing worker from becoming an execution authority.

## Provider neutrality

The worker depends on `AIService`, not on a concrete provider. Provider selection remains owned by the existing AI layer.

## Safety boundary

- provider output is not authority;
- provider output is not truth;
- a tool request is not execution;
- parsing failures become explicit autonomous worker failure results;
- execution remains outside the reasoning worker.
