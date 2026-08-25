# JARVIS Memory Architecture

## Purpose

JARVIS Memory stores structured knowledge about the user, skills, preferences, goals, and system state.

Memory is intentionally distinct from raw conversation history:
- **Conversation History** tracks turn-by-turn interactions ("what was said").
- **Structured Memory** stores persistent claims ("what JARVIS knows").
- **Evidence** connects claims back to exact source statements ("why JARVIS knows it").

---

## Memory Subsystem Components

```text
                     Conversation Turn
                             |
                   Memory Formation Engine
                 (src/memory/memory_formation.py)
                             |
                +------------+------------+
                |                         |
         Candidate Claims             Validation
                |                         |
                +------------+------------+
                             |
                       Deduplication
                             |
             +---------------+---------------+
             |                               |
      Structured Memory               Memory Evidence
   (src/memory/memory_store.py)   (src/memory/evidence_store.py)
             |                               |
             +---------------+---------------+
                             |
                      Memory Retrieval
             (src/memory/memory_retrieval.py)
                             |
                      Context Builder
               (src/context/context_builder.py)
```

---

## Pipeline Flow

1. **Extraction**: `extract_candidates()` extracts structured candidate memories from conversation turns using rules/heuristics.
2. **Validation**: `validate_memory()` enforces category rules, confidence bounds, and importance levels.
3. **Deduplication**: `find_active_memory()` checks for existing active memory keys. Existing claims receive `CORROBORATING` evidence instead of duplicating entries.
4. **Persistence**: New memories enter `memories` with `DIRECT` evidence added to `memory_evidence`.
5. **Retrieval**: `search_memories()` ranks active memories by text relevance, importance, and confidence for context injection.