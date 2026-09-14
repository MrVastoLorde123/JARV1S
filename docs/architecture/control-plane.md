# JARVIS Control Plane

The control plane is the deterministic boundary between intelligence proposals and system authority. Models, agents, UI components, and external inputs may propose work or report observations; the control plane owns what is actually authorized, executed, verified, persisted, and presented as fact.

## Goals

- Present one coherent operational state across interface, runtime, agents, tools, models, and verification.
- Keep authority, permission, execution, and completion claims outside the model.
- Make consequential work traceable through proposal, authorization, execution, observation, verification, and final claim.
- Keep agents and models replaceable without changing JARVIS authority semantics.
- Keep operational state restart-safe and durable.
- Expose useful backend activity without exposing private model chain-of-thought.

## Runtime boundary

The cockpit consumes a read-only `control-plane.v1` snapshot. It does not write state into that snapshot and it must not infer authority from connectivity, model availability, or capability inventory.

The snapshot contains:

- runtime availability and world observation;
- task state and progress;
- active agents;
- pending approvals;
- tool inventory and risk/confirmation declarations;
- model/provider state backed by a live local `/v1/models` observation;
- blockers and errors;
- verification state and evidence references;
- bounded operational events;
- a monotonic observation cursor.

Some fields may temporarily report `NOT_REPORTED` or an empty collection while their deeper runtime projection is not yet wired. Empty data is not a claim that the underlying system has no such state.

## Current runtime projections

The local runtime currently projects:

- concrete active `AgentEntity` instances from `JARVISRuntime.world_runtime`;
- the registered `ToolDefinition` catalog from the runtime's `ToolRegistry`;
- pending coding authorization state from `CodingAgentConfirmationService`;
- local model/provider health from the configured OpenAI-compatible `/v1/models` endpoint.

The task and verification projections remain explicitly `NOT_REPORTED` until their authoritative runtime contracts are wired. They are not inferred from model output, approval existence, or tool inventory.

## Action lifecycle

```text
intent
  -> interpretation
  -> proposal
  -> authorization decision
  -> capability/tool execution
  -> observed result
  -> verification
  -> durable state update
  -> user-visible claim
```

The model never collapses these stages into a single success claim. A response from a model is not evidence that a tool ran, permission exists, or a task completed.

## Event visibility

The UI may display operational events such as request received, authorization decisions, tool start/completion/failure, model response received, verification started/completed/failed, pauses, resumes, cancellations, and runtime errors. Private chain-of-thought is not a required dependency of the control plane.

## Transport

The local runtime exposes the control plane as a read-only HTTP resource:

`GET /api/control-plane`

Optional query parameters:

- `after_cursor`: return events after a previously consumed cursor;
- `limit`: bound the returned event window.

The local launcher uses port `8768` for the control-plane transport. The existing world, command, and capability transports remain separate boundaries.

## Acceptance criteria

The control plane is mature when:

- the UI renders runtime-owned truth without local fabrication;
- users can see what JARVIS is doing, waiting for, blocked by, and verifying;
- execution results are distinguishable from model claims;
- authority is never implied by observation or capability discovery;
- the event cursor supports incremental observation;
- restart/reload preserves durable state owned by the runtime;
- models can be swapped without changing authority or persistence semantics;
- deterministic tests can exercise the boundary without requiring an LLM.
