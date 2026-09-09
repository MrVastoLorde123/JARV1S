# Decision 199 — V2 Rich Interface Cockpit

Status: IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose

V2 makes the human interface the primary development surface. The interface should make JARVIS visible as a living personal intelligence system rather than presenting a conventional SaaS dashboard.

## Product map

The first five spaces are HOME, WORK, MIND, CAPABILITIES, and SELF.

- HOME is the living state of JARVIS: presence, cognitive activity, current focus, recent intelligence, projects, and conversation.
- WORK exposes active work, progress, waiting conditions, and long-running work state.
- MIND exposes personal memory and knowledge as an evidence-aware second brain rather than raw database records.
- CAPABILITIES exposes declared abilities and their state, including tools and models without giving them authority.
- SELF exposes JARVIS architecture, versions, performance, memory, learning, security, health, updates, and experiments.

## Technical boundary

```text
Human
  ↓
Web UI (React / TypeScript)
  ↓
JARVIS Gateway / Interface Contract
  ↓
API + Event Stream
  ↓
JARVIS Core
```

The frontend knows stable interface contracts and presentation models, not Python internals. REST is suitable for request/response state; WebSocket or SSE is suitable for live activity and status updates.

## Design direction

The interface is calm, information-dense, and alive without decorative animation. System state is expressed through subtle presence, activity, progress, and status signals. Conversation is central, but the interface does not collapse JARVIS into a chat application.

## Explicit non-powers

```text
Interface ≠ Authority
Interface ≠ Orchestration
Interface ≠ Executor
Interface ≠ Authorization
Interface ≠ Persistence
Interface ≠ AI Provider
Interface ≠ Truth / Certainty
```

## First implementation

A Vite + React + TypeScript UI shell lives under `ui/`. It establishes the visual language, five-space navigation, conversation composer, recent intelligence, project state, capability state, and self/mind placeholders using provider-neutral TypeScript contracts.

Runtime integration is deliberately deferred to the gateway/API boundary. No UI component calls Python services, tools, policies, authorization, or model providers directly.

## Completion criterion

The cockpit is complete when it consumes stable gateway contracts, receives live activity/status events, renders the five spaces from real JARVIS state, provides conversation/task interaction, and remains replaceable without changes to core authority semantics.
