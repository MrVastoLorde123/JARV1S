# JARVIS Architecture Overview

JARVIS is a persistent personal intelligence and agency system. It is not a chatbot wrapper and it is not defined by any single model or provider.

## Core Principle

> **JARVIS is the system. AI is a capability.**

The system owns durable state, context, authority, capabilities, execution, and orchestration. AI models provide intelligence inside those boundaries.

## Major Layers

```text
Knowledge
   ↓
Context
   ↓
Intelligence
   ↓
Authority
   ↓
Agency
   ↓
Capabilities / Plugins
   ↓
External World
```

### Knowledge

Memory, evidence, provenance, and durable project information.

### Context

Working context assembled for a task. Context selection and composition remain provider-neutral.

### Intelligence

AI-assisted reasoning, interpretation, prioritization, planning, and other cognitive capabilities.

### Authority

The deterministic semantic pipeline established by M7. It decides whether a proposed action is valid, permitted, confirmed where required, authorized, and ready for execution handoff.

### Agency

The post-M7 runtime that turns an authorized handoff into real execution, observes outcomes, and records result/error state. This is the focus of M8.

### Capabilities / Plugins

Concrete abilities exposed to JARVIS, such as filesystem operations, browsing, APIs, automation, and future integrations.

## M7 Boundary

```text
Reasoning
  ↓
Interpretation
  ↓
Prioritization
  ↓
Proposal
  ↓
Validation
  ↓
Policy
  ↓
Confirmation
  ↓
Confirmation Integrity
  ↓
Authorization
  ↓
Authorization Integrity
  ↓
Execution Preparation / Handoff
```

M7 ends here. No M7.11 is defined.

## Architectural Invariants

```text
Interpretation ≠ Truth
Validation ≠ Authorization
Confirmation ≠ Authorization
Authorization ≠ Execution
Integrity ≠ Authority
READY ≠ EXECUTED
```

These boundaries allow JARVIS to become more capable without letting a model, plugin, worker, or interface silently become the source of authority.
