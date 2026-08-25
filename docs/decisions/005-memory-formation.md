# ADR-005: Automated Memory Formation Pipeline

## Status

Accepted

## Context

Previously, JARVIS could only retrieve memories manually created or pre-seeded in the database.
To become a persistent companion that evolves alongside the user, JARVIS must maintain its own structured knowledge base automatically from active conversations.

However, an AI model should not blindly store every sentence as absolute truth.

## Decision

Memory formation will operate as an explicit pipeline controlled by JARVIS, separate from the AI provider:

```text
Conversation Turn (User + Assistant)
         |
Candidate Extraction (Deterministic rules / heuristics)
         |
Validation (Schema, bounds & category constraints)
         |
Deduplication (Key matching against active memories)
         |
  +------+------+
  |             |
New Memory   Corroborating Evidence
  +------+------+
         |
Memory Store + Evidence Store
```

1. **Decoupled Engine**: The AI provider only produces response text. JARVIS runs `process_turn()` after each conversation turn.
2. **Rule-Based Extraction (V1)**: Conservative, deterministic keyword triggers scan assistant output for claims (skills, preferences, goals, projects, personal facts, workflows).
3. **Evidence Provenance**: Every created memory is linked with `DIRECT` evidence referencing the source text. Duplicate claims add `CORROBORATING` evidence to existing active memories instead of cluttering the store.
4. **Opt-In Core Trigger**: `JARVIS(enable_memory_formation=True)` activates the post-turn pipeline on demand.

## Consequences

- JARVIS evolves its structured memory dynamically as conversations progress.
- Spurious or false memories are prevented through strict validation and conservative extraction.
- Provenance is preserved so every memory can be traced back to its supporting evidence in conversation history.
