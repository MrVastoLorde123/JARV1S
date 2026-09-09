# Decision 0202 — V2 Interface Personality and Self-Observability

**Status:** IMPLEMENTED IN M27.10 / AWAITING LOCAL VERIFICATION

## Purpose

The V2 interface should become a functional operating environment with a recognizable JARVIS personality. Visual choices must improve readability, orientation, state awareness, and interaction rather than exist for decoration.

## Navigation

The primary navigation is a collapsible vertical sidebar. Expanded mode provides labels and system context; collapsed mode preserves icon-based navigation while reclaiming horizontal space.

## Typography

Typography uses a readable humanist system stack for primary interface text and a restrained monospace stack for telemetry, labels, states, and system metadata. Text contrast must remain readable against the dark interface and should not rely on dim gray text for hierarchy.

## State presence

JARVIS state is represented by compact, state-aware visual signals rather than noisy status sentences. The interface should communicate presence through changing state, motion, focus, and contextual status while remaining calm and functional.

## SELF

SELF is an observability surface for JARVIS's internal activity. It may expose:

- thinking and reasoning state;
- delegation and model-task preparation;
- communication/context handoff;
- model role and current task state;
- CPU, memory, and GPU pressure;
- active model task count and concurrency strategy;
- resource guard behavior.

These displays represent system state and must not create new authority in the renderer.

## Model coordination

JARVIS model coordination defaults to sequential task handoff. A second model should begin only after the prior task has completed unless the system can prove that limited concurrency is safe and useful. Resource pressure must be observable and capable of reducing or preventing additional model work.

The interface therefore exposes resource pressure and model coordination as state, while actual scheduling and authorization remain backend responsibilities.

## Invariants

- Interface personality never redefines JARVIS authority.
- Visual state is derived from real or explicitly identified demo state.
- Self-observability does not imply privileged control.
- Resource-aware scheduling remains a backend concern.
- One-by-one model handoff is the safe default until concurrency is justified.
