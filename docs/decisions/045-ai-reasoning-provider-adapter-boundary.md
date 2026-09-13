# Decision 045 — AI Reasoning Provider Adapter Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a provider-neutral adapter that turns an existing `AIService` into the reasoning callable consumed by `AutonomousReasoningWorker`.

The adapter:

- builds an `AIRequest` from the current `AutonomousJob`;
- includes the job goal and working context as reasoning input;
- calls the existing `AIService` rather than a concrete provider;
- returns the provider response content unchanged to the reasoning worker for structured action decoding;
- preserves provider/model metadata separately from the reasoning action;
- does not invoke tools, grant authority, persist jobs, or choose provider-specific transport behavior.

## Prompt/contract boundary

The adapter is responsible only for constructing the provider-neutral request. It does not decide whether a requested action is authorized or executable.

## Safety boundary

- AI capability is not authority.
- Provider output is not truth.
- A model response is not execution.
- Tool requests remain proposals until a later execution boundary interprets them through existing deterministic controls.
