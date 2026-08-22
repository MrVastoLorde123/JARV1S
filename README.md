# JARVIS PREMATURE

> A personal AI system built around persistent memory, evidence, context, retrieval, and tools.

JARVIS is an experimental personal AI system designed to grow beyond a traditional chatbot.

The goal is not to create another interface for an LLM.

The goal is to build the **system surrounding the AI**:

```text
Data
  ↓
Ingestion
  ↓
Normalization
  ↓
Storage
  ↓
Retrieval
  ↓
Memory + Evidence
  ↓
Context
  ↓
AI
  ↓
Reasoning
  ↓
Actions / Tools
```

The AI model is replaceable.

The underlying knowledge, memory, evidence, retrieval, and context systems belong to JARVIS.

---

# 1. Project Philosophy

JARVIS is being developed with one primary principle:

> **Build the system first. Let the AI sit inside the system rather than making the AI the system.**

An LLM can reason extremely well, but it should not be treated as:

- the database
- the source of truth
- the memory store
- the retrieval engine
- the provenance system
- the application architecture

Instead, JARVIS should provide the AI with structured, relevant, traceable information.

This creates a separation between:

```text
JARVIS
├── Data
├── Memory
├── Evidence
├── Retrieval
├── Context
├── Tools
└── AI Provider
```

The AI provider can change without requiring the entire JARVIS system to be rebuilt.

---

# 2. The Core Architectural Idea

The current architectural direction is:

```text
OpenAI Raw History
        ↓
Conversation Ingestion
        ↓
SQLite
        ├── Conversations
        ├── Messages
        └── Full-Text Search
        ↓
Structured Memories
        ↓
Evidence / Provenance
        ↓
Retrieval
        ↓
Context Package
        ↓
AI / Reasoning
        ↓
Actions
```

This architecture deliberately separates **source information** from **derived information**.

Raw information should remain available.

Memories are derived from information.

Evidence connects derived information back to its source.

Context is assembled for a particular AI request.

The AI reasons over that context.

---

# 3. Raw Data

Raw data is the foundation.

For example:

```text
OpenAI export
     ↓
raw/
     ↓
parser
     ↓
normalized database
```

The original source should be preserved rather than immediately converted into AI-generated summaries.

Why?

Because a generated memory can be wrong.

If the original source still exists, JARVIS can:

1. inspect the original information
2. verify the memory
3. regenerate derived information
4. improve the memory system later
5. migrate the schema without losing the source

This gives JARVIS a recoverable foundation.

---

# 4. Ingestion

The ingestion system converts external information into data JARVIS can work with.

The general principle is:

```text
SOURCE
  ↓
PARSE
  ↓
NORMALIZE
  ↓
STORE
  ↓
INDEX
```

Ingestion should ideally be:

- repeatable
- deterministic where possible
- safe
- observable
- migration-friendly
- resistant to duplication

Re-importing an updated OpenAI export should be treated as a normal operation.

The architecture should not depend on a source file being imported only once.

---

# 5. Conversation Storage

OpenAI conversation history is not simply treated as a collection of prompts.

It becomes searchable source material.

The current direction uses SQLite for local structured storage.

Conceptually:

```text
SQLite
├── conversations
├── messages
├── memories
├── evidence
└── indexes
```

Full-text search allows JARVIS to locate relevant historical conversations without requiring the AI model to read the entire history every time.

This is important because:

> **Retrieval should happen before context assembly.**

JARVIS should retrieve what is relevant rather than blindly dumping everything into the model.

---

# 6. Memory

Memory is information that JARVIS has determined is worth retaining beyond the immediate interaction.

The initial memory taxonomy is locked as:

```text
PERSONAL
SKILL
PREFERENCE
PROJECT
GOAL
FACT
WORKFLOW
RELATIONSHIP
EXPERIENCE
OTHER
```

These categories provide an initial structure for persistent knowledge.

Memory should not simply mean:

> "Something the AI once said."

Instead, memory should represent information JARVIS has chosen to preserve.

---

# 7. Memory Is Not Evidence

A critical architectural distinction:

```text
MEMORY ≠ EVIDENCE
```

A memory is a derived representation.

Evidence is the information supporting that representation.

For example:

```text
Memory:
User is building JARVIS.

Evidence:
Conversation #123
Message #456
```

This distinction allows JARVIS to answer:

> "Why does JARVIS believe this?"

rather than merely:

> "JARVIS believes this because the database says so."

---

# 8. Memory Provenance

Memories should retain provenance whenever practical.

Conceptually:

```text
Memory
   ↓
Evidence
   ↓
Source
   ↓
Original Data
```

This creates an audit trail.

The objective is not perfect academic citation of every sentence.

The objective is **traceability**.

If a memory is incorrect, JARVIS should eventually be able to identify where that memory came from.

---

# 9. Memory Retrieval

Memory retrieval is intentionally separated from AI reasoning.

The retrieval layer should retrieve information.

The AI should reason over retrieved information.

These are different responsibilities.

The current direction uses deterministic, read-only memory retrieval.

Conceptually:

```text
Query
 ↓
Memory Retrieval
 ↓
MemoryResult
 ↓
Context Assembly
 ↓
AI
```

Retrieval should not secretly mutate memory.

That separation makes the system easier to test and reason about.

---

# 10. Relevance, Confidence, and Importance

These concepts should not be collapsed into one score.

### Relevance

How useful is this memory for the current query?

### Confidence

How trustworthy is the memory?

### Importance

How important is the memory to the user's long-term context?

These represent different dimensions.

For example:

```text
Memory A
Relevance: HIGH
Confidence: HIGH
Importance: LOW

Memory B
Relevance: HIGH
Confidence: LOW
Importance: HIGH
```

Combining everything into one number can hide important information.

The retrieval architecture therefore keeps these concepts separate.

---

# 11. ACTIVE Memory

Memory can have lifecycle state.

The current direction includes filtering for active memories.

Conceptually:

```text
ACTIVE
INACTIVE / ARCHIVED
```

Inactive memories should not automatically appear in normal retrieval.

This allows JARVIS to retain historical information without treating every historical statement as current truth.

---

# 12. Context

Memory and context are not the same thing.

Memory is persistent.

Context is assembled for a particular operation.

For example:

```text
Persistent Memory
        ↓
   Retrieval
        ↓
Relevant Memories
        ↓
Context Package
        ↓
AI Request
```

A memory can exist for years without being included in every AI request.

Context should be **task-specific**.

---

# 13. ContextPackage

The context layer should remain provider-neutral.

A `ContextPackage` represents information JARVIS has assembled for an AI operation.

It can contain bounded groups such as:

```text
MEMORY
EVIDENCE
HISTORY
```

along with metadata relevant to privacy and provenance.

Conceptually:

```text
ContextPackage
├── memories
├── evidence
├── history
├── provenance
└── privacy metadata
```

The context layer should not depend on a specific AI provider.

---

# 14. Deterministic Context Assembly

Context assembly should be deterministic wherever possible.

The same retrieval inputs should produce predictable context.

The context layer should not contain hidden AI reasoning.

It should not depend on:

- OpenAI-specific objects
- model-specific request structures
- tokenization logic
- provider-specific APIs

Those concerns belong at the AI adapter/integration boundary.

This keeps the core JARVIS architecture provider-neutral.

---

# 15. Retrieval Before Generation

One of the central principles of JARVIS is:

> **Retrieve first. Generate second.**

Instead of:

```text
User
 ↓
LLM
 ↓
"Maybe I remember..."
```

the intended architecture is:

```text
User
 ↓
JARVIS Retrieval
 ↓
Relevant Data
 ↓
Memory + Evidence + History
 ↓
Context
 ↓
LLM
 ↓
Answer
```

The model therefore receives information deliberately selected by the system.

---

# 16. AI Provider Independence

JARVIS should surround the AI rather than depend completely on it.

Conceptually:

```text
              ┌───────────────┐
              │   OpenAI      │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │      AI        │
              │    Adapter     │
              └───────┬───────┘
                      │
        ┌─────────────▼─────────────┐
        │          JARVIS           │
        │                           │
        │ Data                      │
        │ Memory                    │
        │ Evidence                  │
        │ Retrieval                 │
        │ Context                   │
        │ Tools                     │
        └───────────────────────────┘
```

The AI model can eventually be:

- OpenAI
- a local model
- another cloud provider
- a future model that does not yet exist

The JARVIS foundation should remain useful.

---

# 17. Why This Architecture?

The architecture exists to solve several fundamental problems.

### Problem: AI forgets

**Solution:** persistent external memory.

### Problem: AI context windows are limited

**Solution:** retrieval and bounded context assembly.

### Problem: AI-generated memories can be wrong

**Solution:** evidence and provenance.

### Problem: AI providers change

**Solution:** provider-neutral JARVIS core.

### Problem: historical data is difficult to search

**Solution:** structured storage + full-text search.

### Problem: memory becomes stale

**Solution:** memory lifecycle/state.

### Problem: systems become impossible to debug

**Solution:** separation of data, retrieval, context, and generation.

---

# 18. Long-Term Vision

JARVIS is intended to eventually become more than a local memory database.

A possible future architecture is:

```text
                    JARVIS SERVER
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Database           AI              Tools/API
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
             PC        Phone      Browser
```

The long-term concept is a central JARVIS system that can provide persistent context across devices.

A dedicated JARVIS Server could eventually manage:

- databases
- AI providers
- memory
- retrieval
- tools
- APIs
- authentication
- synchronization

A portable USB deployment is a possible future deployment target, but is not the immediate architectural priority.

Privacy boundaries may eventually separate private local context from external AI services.

---

# 19. What JARVIS Should Eventually Be Able To Answer

The deeper purpose of the architecture is to allow JARVIS to answer questions such as:

> **What do I know?**

> **Where did I learn it?**

> **How reliable is it?**

> **Is it still current?**

> **What context is relevant right now?**

> **What evidence supports this?**

> **What should be remembered?**

> **What should be forgotten, archived, or updated?**

Those questions are more important than simply producing a convincing AI response.

---

# 20. Current Development Priority

The project should be developed incrementally.

Current foundation:

```text
RAW DATA
   ↓
INGESTION
   ↓
STORAGE
   ↓
SEARCH
   ↓
MEMORY
   ↓
EVIDENCE
   ↓
RETRIEVAL
   ↓
CONTEXT
   ↓
AI
```

Higher-level capabilities should be built on this foundation.

Do not prematurely optimize for:

- autonomous agents
- complex tool ecosystems
- voice interfaces
- SaaS deployment
- multi-agent systems
- elaborate UI
- distributed infrastructure

Those may become useful later.

The foundation comes first.

---

# 21. Development Philosophy

JARVIS should favor:

- solid architecture over rushed implementation
- understanding over blindly copying code
- reusable components over unnecessary reinvention
- explicit decisions over hidden behavior
- tests over assumptions
- evidence over unsupported claims
- migrations over destructive changes
- simple foundations before complex abstractions

The system should be understandable by the person building it.

The purpose is not merely to make JARVIS work.

The purpose is to understand **why it works**.

---

# 22. Project Status

JARVIS is currently in active development.

Established areas include:

- project architecture
- OpenAI conversation ingestion
- raw data preservation
- SQLite-based storage direction
- full-text search
- structured memory
- memory taxonomy
- evidence/provenance concepts
- deterministic memory retrieval
- memory lifecycle concepts
- provider-neutral context
- `ContextPackage`
- context assembly principles
- testing and validation of the developing architecture

The architecture will continue to evolve, but established decisions should not be changed casually.

Significant architectural changes should be documented with:

1. the existing design
2. the problem
3. the proposed change
4. the reasoning
5. migration impact
6. testing requirements

---

# 23. Design Decisions

JARVIS maintains an explicit distinction between:

| Layer | Responsibility |
|---|---|
| Raw Data | Preserve original information |
| Ingestion | Convert external sources into structured data |
| Storage | Persist structured information |
| Search | Locate relevant source material |
| Memory | Preserve useful long-term knowledge |
| Evidence | Support and trace memories |
| Retrieval | Select relevant information |
| Context | Assemble information for an operation |
| AI | Reason/generate |
| Tools | Perform actions |

The separation of these layers is one of the most important architectural principles in the project.

---

# 24. Design Thinking Archive

This section is intentionally part of the README.

JARVIS is not only a codebase.

The reasoning behind the architecture is part of the project's knowledge.

Important design questions and explanations should be preserved here as the project evolves.

Future entries should document questions such as:

- Why is raw data preserved?
- Why is memory separate from context?
- Why is evidence separate from memory?
- Why should retrieval be deterministic?
- Why should relevance, confidence, and importance remain separate?
- Why should context assembly be provider-neutral?
- Why should tokenization remain outside the context layer?
- Why does JARVIS need full-text search?
- Why should AI providers be replaceable?
- How should memory updates work?
- How should stale memories be handled?
- How should conflicting memories be resolved?
- How should evidence affect confidence?
- How should ingestion remain idempotent?
- How should schema migrations work?
- What should JARVIS remember automatically?
- What should require confirmation?
- What information should never become permanent memory?

These explanations should be treated as architectural documentation, not merely conversation history.

---

# 25. The Core Idea

JARVIS is ultimately an attempt to construct a system around intelligence.

The model provides reasoning.

JARVIS provides:

```text
continuity
+
memory
+
evidence
+
retrieval
+
context
+
tools
+
data ownership
```

The long-term objective is a system where the AI does not need to pretend that it remembers.

It can actually retrieve what matters.

And when it does, JARVIS should be able to explain **where that information came from and why it was provided.**

---

## Status

**Project:** JARVIS PREMATURE  
**Stage:** Active development  
**Architecture:** Evolving  
**Primary focus:** Data → Memory → Evidence → Retrieval → Context → AI