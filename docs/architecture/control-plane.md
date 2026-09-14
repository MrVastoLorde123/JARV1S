# JARVIS Control Plane

## Purpose

The JARVIS control plane is the deterministic boundary between intelligence proposals and system authority. Models, agents, UI components, and external inputs can propose work or report observations; the control plane owns what is actually authorized, executed, verified, persisted, and reported as fact.

## North-star goals

1. Present one coherent operational state across the interface, runtime, agents, tools, models, and verification.
2. Keep authority, permissions, execution, and completion claims outside the model.
3. Make every consequential action traceable through proposal, authorization, execution, observation, verification, and final claim.
4. Make agent and model implementations replaceable without changing JARVIS authority semantics.
5. Make operational state durable and restart-safe.
6. Expose useful backend activity to the user without exposing private model chain-of-thought.

## Control-plane layers

### Interface

The interface is a cockpit over runtime truth. It may submit user intent and render state, events, blockers, approvals, tool activity, model activity, and verification evidence. It must not invent state locally.

### Runtime

The runtime owns lifecycle, task state, scheduling, persistence, authorization decisions, capability grants, execution coordination, retry policy, and completion state.

### Agents

Agents are bounded workers. They may reason, produce proposals, request capabilities, report observations, and return results. Agent-originated permission claims are advisory input only; they cannot grant authority to themselves or other agents.

### Models

Models provide intelligence. A model may propose a plan, classify intent, summarize evidence, generate code, or request capabilities. A model response is never evidence that an external action occurred, that permission exists, or that a task is complete.

### Evidence and verification

Execution produces observations/results. Verification evaluates those observations against explicit contracts. JARVIS may claim completion only after the required verification boundary has passed.

## Canonical action lifecycle

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

A failure at any stage is represented explicitly. The system must not collapse a proposal, authorization, execution result, or verification result into one generic success flag.

## Canonical control snapshot

The future cockpit should consume a single runtime-owned snapshot containing, at minimum:

- system/runtime availability
- active task or mission
- task lifecycle state and progress
- active agents and their lifecycle state
- pending capability/approval requests
- recent tool invocations and results
- active model/provider and model response status
- blockers and errors
- verification status and evidence references
- durable observation/event cursor or sequence

This snapshot is read-only from the UI. Mutations occur through explicit runtime commands and capability boundaries.

## Event visibility

The UI should display operational events, not hidden reasoning. Useful events include request received, plan proposed, capability requested, authorization granted/denied, tool started/completed/failed, model response received, verification started/completed/failed, task paused/resumed/cancelled, and runtime errors.

Private chain-of-thought is never a required UI dependency.

## Model routing contract

Model selection is a runtime concern. The router may choose a model based on task role, measured fitness, latency, availability, context requirements, and policy. The selected model does not receive additional authority because it was selected.

Role fitness is empirical and replaceable. No model becomes a permanent authority-bearing component merely because it has the highest benchmark score.

## Acceptance criteria for the control plane

The control plane is mature when:

- the UI can render runtime truth without local fabrication;
- a user can see what JARVIS is doing, waiting for, blocked by, and verifying;
- every tool action has an explicit authorization boundary;
- execution results are distinguishable from model claims;
- verification is required before completion claims where the contract demands it;
- restart/reload restores durable operational state;
- models can be swapped without changing authority or persistence semantics;
- tests can exercise these boundaries deterministically without requiring an LLM.
