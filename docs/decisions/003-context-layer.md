# ADR-003: Introduce a Dedicated Context Layer

## Status

Accepted

## Decision

Context preparation will be handled by a dedicated Context Builder rather than by the AI provider or memory subsystem.

## Reason

The context layer provides a stable boundary between JARVIS knowledge and intelligence providers.

It allows JARVIS to control:

- relevance
- evidence
- limits
- privacy metadata
- provenance

without making the AI provider responsible for retrieving JARVIS data.