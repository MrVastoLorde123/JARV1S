# ADR-005: Automated Memory Formation Pipeline

## Status

Accepted — V1

## Context

JARVIS initially stored and retrieved memories that were created explicitly.

To become a persistent personal AI system, JARVIS eventually needs to identify information from conversations that may be worth retaining.

However, automatically storing every model-generated statement would create a dangerous feedback loop:

```text
AI says something
    ↓
JARVIS stores it
    ↓
JARVIS retrieves it later
    ↓
AI sees its previous claim
    ↓
claim appears increasingly trustworthy