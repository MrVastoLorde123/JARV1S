# JARVIS Context Architecture

## 1. Purpose

The Context Layer (`src/context/`) acts as a strict boundary between JARVIS Knowledge (memories, evidence, conversation state, history) and AI Intelligence Providers.

It ensures:
1. AI providers receive only provider-neutral, formatted data structures (`ContextPackage`).
2. JARVIS maintains deterministic bounds over token usage, item limits, and privacy metadata.
3. The context creation step remains **READ-ONLY**—it never modifies database state or triggers side effects.

---

## 2. Context Builder Pipeline Flow

```text
User Query + ContextOptions + StateSnapshot
                    │
                    ▼
            [ build_context() ]
       (src/context/context_builder.py)
                    │
   +----------------+----------------+
   │                │                │
Memory Search    Evidence Fetch   State Items
(search_memories) (get_evidence)  (recent turns & topic)
   │                │                │
   +----------------+----------------+
                    │
                    ▼
             ContextPackage
        (items, instructions, metadata)
```

---

## 3. Core Data Structures

- **`ContextItem`** ([`src/context/models.py`](file:///c:/Users/jeoop/PycharmProjects/JARV1S/src/context/models.py)):
  A single piece of information injected into context:
  - `source_type`: `MEMORY`, `EVIDENCE`, `HISTORY`, or `STATE`.
  - `content`: Plaintext text representation.
  - `relevance_score`: Relevance score between 0.0 and 1.0.
  - `confidence` / `importance`: Scoring parameters from structured memory.
  - `privacy_level`: Metadata marker (`PRIVATE`, `INTERNAL`, `PUBLIC`).
  - `provenance`: Traceability dict containing `memory_id`, `conversation_id`, or `turn_timestamp`.

- **`ContextOptions`**:
  Configurable limits:
  - `max_memories` (default: 10)
  - `max_evidence` (default: 20)
  - `max_history` (default: 30)
  - `max_state_turns` (default: 10)
  - Flags for enabling/disabling specific source types (`include_memories`, `include_state`, etc.).

- **`ContextPackage`**:
  The complete immutable package containing query, tuple of `ContextItem`s, default system instructions, and builder metadata.