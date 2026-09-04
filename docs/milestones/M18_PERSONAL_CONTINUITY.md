# M18 — Personal Continuity

## Goal

Make JARVIS continuous across interactions and local runtime restarts without
creating a second semantic or authority system.

```text
Human Operating Layer
        ↓
Persistent Session Identity
        ↓
Durable Session / Conversation
        ↓
Existing Memory + Evidence + Context
        ↓
Existing Intelligence
```

## Slices

### M18.1 — Persistent Session Identity

The human-facing session identifier survives local process restarts. `:new`
creates and persists a new identity. The identifier is continuity metadata only.

### M18.2 — Durable Conversation Resume

The existing `DurableSessionRuntime` and `ConversationStore` are wired into the
local runtime so a resumed session restores its prior conversation state.

### M18.3 — Cross-Process Context Continuity

Restored conversation turns remain provider-neutral context and flow through
the existing context pipeline. No provider receives raw persistence access.

### M18.4 — Personal Memory Formation

The local personal runtime enables the existing memory-formation path so useful
facts, preferences, projects, goals, experiences, and other bounded memories can
be persisted and recalled through the existing memory/context layers.

### M18.5 — Session Isolation

Starting a new session creates a new conversation identity and does not inherit
conversation state from the previous session.

### M18.6 — Continuity Contract Tests

Tests verify identity persistence, restart behavior, durable conversation
binding, and session isolation.

### M18.7 — Continuity Integration

The local launcher composes the complete M18 path without bypassing the
canonical runtime or changing authority boundaries.

## Boundaries

- Continuity ≠ Authority
- Memory ≠ Truth
- Conversation ≠ Policy
- Session Identity ≠ Authorization
- Persistence ≠ Permission
- Recall ≠ Intent
- Context ≠ Instruction
- Knowledge ≠ Policy
- Provider ≠ JARVIS
- Learning ≠ Authorization

## Completion condition

A user can close and reopen the local JARVIS process, retain the same persisted
session identity, and continue the prior conversation through the canonical
runtime. Starting a new session explicitly isolates the new conversation while
leaving prior persistent data intact.

## Non-goals

M18 does not introduce autonomous initiative, long-horizon planning, new policy,
authorization, execution authority, external web retrieval, or a second memory
engine. Those concerns remain in their existing bounded layers or future
milestones.
