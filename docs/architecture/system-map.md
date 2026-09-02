# JARVIS System Map

JARVIS is organized around a deliberate separation of concerns. The system owns state, authority, capabilities, and orchestration; AI models are used as capabilities inside those boundaries.

```text
                              JARVIS
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
          KNOWLEDGE            CONTEXT           INTELLIGENCE
             │                   │                   │
      Memory / Evidence     WorkingContext       AI / Reasoning
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                         AUTHORITY PIPELINE
                                 │
           Reason → Interpret → Prioritize → Propose
                                 │
                 Validate → Policy → Confirm
                                 │
             Integrity → Authorize → Integrity
                                 │
                         Execution Handoff
                                 │
                           AGENCY RUNTIME
                                 │
                     Plugin / Capability Layer
                                 │
                       Workers (future M9)
                                 │
                            External World
```

## Subsystem Responsibilities

### Knowledge

Stores durable information and evidence. Knowledge should preserve provenance and distinguish persisted claims from observations and derived interpretations.

### Context

Builds the provider-neutral working state required for a particular task. Context composition is separate from AI provider selection.

### Intelligence

Models and reasoning mechanisms interpret context, generate proposals, prioritize information, and help JARVIS think. Intelligence does not receive authority merely by producing an answer.

### Authority

M7 is the deterministic authority layer. It converts proposals into execution-ready handoffs only when the required validation, policy, confirmation, authorization, and integrity conditions are satisfied.

### Agency

M8 is responsible for executing an authorized handoff and observing the outcome. It owns controlled invocation and result/error lifecycle semantics.

### Capabilities / Plugins

Capabilities expose concrete abilities such as browsing, filesystem work, automation, APIs, or future integrations. They should remain replaceable and independently bounded.

### Workforce

M9 can introduce workers as bounded execution participants. Workers should consume assignments and capabilities, produce observable work, and remain inside JARVIS's authority and execution boundaries.

## Core Principle

> **JARVIS is the system. AI is a capability.**

This principle prevents a model, plugin, worker, or interface from silently becoming the system's source of truth or authority.
