# Decision 043 — Autonomous Reasoning Action Boundary

## Status

Proposed V1 application/runtime boundary.

## Decision

Introduce a provider-neutral structured reasoning action contract between the AI layer and the autonomous job runtime.

A reasoning cycle may produce exactly one next disposition:

- `CONTINUE` — continue autonomous reasoning without side effects.
- `TOOL_REQUEST` — request one existing JARVIS tool invocation.
- `WAIT_AUTHORIZATION` — stop until an existing authority/confirmation boundary is satisfied.
- `WAIT_INPUT` — stop until required user input exists.
- `WAIT_TOOL` — stop until an external tool/dependency result is available.
- `COMPLETE` — finish the job with a result.
- `FAIL` — finish the job as failed with explicit reason.

The contract carries no permission and does not invoke tools. It is interpreted by the application runtime, which delegates tool execution to the existing `ToolService` and authority mechanisms.

## Provider neutrality

The action is produced from provider output but is not tied to a specific LLM, model, vendor, or transport. Qwen, OpenAI, Anthropic, local models, and future providers must be able to target the same contract.

## Safety boundary

- A `TOOL_REQUEST` is not authorization.
- A capability listing is not permission.
- A model response is not truth.
- The action parser must reject malformed or ambiguous dispositions.
- Tool execution remains owned by the existing tool service and policy/confirmation layers.
- The reasoning action may never directly mutate authorization, persistence, or execution state.
