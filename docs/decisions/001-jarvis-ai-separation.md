# ADR-001: Separate JARVIS from AI Providers

## Status

Accepted

## Decision

JARVIS will remain independent from any specific AI provider.

AI models are treated as interchangeable capabilities rather than the foundation of the system.

## Reason

This allows JARVIS to:

- use local models
- use cloud models
- switch providers
- route tasks between providers
- operate without an external API

The core architecture therefore remains provider-neutral.