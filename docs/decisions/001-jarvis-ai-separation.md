# ADR 001 — JARVIS / AI Separation

## Decision

JARVIS is the system. AI models are capabilities inside JARVIS rather than the system's identity, authority, or durable state.

JARVIS will use a hybrid cognitive architecture combining deterministic state and contracts with probabilistic methods, search, optimization, memory, knowledge, optional machine learning, and optional language models.

The architecture must remain capable of becoming more intelligent without any model, learning process, plugin, worker, or interface silently becoming more authoritative.

## Rationale

A large trained model is not required for every form of intelligent behavior. JARVIS can explicitly engineer capabilities such as state management, planning, graph reasoning, temporal constraints, evidence tracking, policy boundaries, feedback loops, and selected probabilistic or optimization methods.

Models remain valuable where learned representations or generalization materially improve a capability. They are replaceable components and do not own JARVIS identity.

## Consequences

- learning and intelligence remain separate from authority
- model providers may be replaced without redefining JARVIS
- deterministic contracts can constrain probabilistic and generative components
- future machine learning can be introduced incrementally where beneficial
- proactive cognition can be built without creating an unrestricted autonomous authority path

## Invariants

```text
Model ≠ JARVIS
LLM ≠ JARVIS
Intelligence ≠ Authority
Learning ≠ Authority
Prediction ≠ Permission
Capability ≠ Permission
```
