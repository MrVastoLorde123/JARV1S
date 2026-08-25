# JARVIS

JARVIS is a personal, local-first AI partner designed to grow with its user, retain structured knowledge, use tools, and operate independently of any single AI provider.

The long-term goal is not simply to build a chatbot.

JARVIS is intended to become a persistent technical companion that can evolve alongside its user, technology, and engineering environment.

---

## Current Status

JARVIS is currently in active foundational development.

Implemented:

- OpenAI conversation data ingestion
- Conversation database
- Full-text message search
- Structured memory
- Memory validation and deduplication
- Evidence and provenance
- Memory retrieval
- Context building
- Conversation state tracking & bounded context V1
- Automated memory formation pipeline
- Provider-neutral AI interface
- AI service / provider orchestration
- Local AI provider
- llama.cpp integration
- Qwen3-4B local inference
- JARVIS Core
- End-to-end local inference

Current local model baseline:

- Model: Qwen3-4B Q4_K_M
- Runtime: llama.cpp
- Backend: CUDA
- Context: 8192 tokens
- GPU: NVIDIA GTX 1650 Ti Max-Q
- RAM: 32 GB

---

## Documentation Index

### 📐 Architecture Guides
- [Architecture Overview](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/achitecture/overview.md) — Subsystem hierarchy & core principles
- [AI Architecture](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/achitecture/ai.md) — Provider-neutral intelligence layer & capabilities
- [Context Architecture](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/achitecture/context.md) — Context builder boundary, options & packages
- [Memory Architecture](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/achitecture/memory.md) — Formation pipeline, retrieval & evidence linking

### 📜 Architecture Decision Records (ADRs)
- [ADR-001: Separate JARVIS from AI Providers](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/001-jarvis-ai-seperation.md)
- [ADR-002: Separate Memory from Evidence](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/002-memory-evidence.md)
- [ADR-003: Introduce a Dedicated Context Layer](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/003-context-layer.md)
- [ADR-004: Local-First AI Development](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/004-local-first-ai.md)
- [ADR-005: Automated Memory Formation Pipeline](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/005-memory-formation.md)

### 🛠️ Developer Setup & Guides
- [Local AI Setup Guide](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/development/local-ai.md) — Server execution, llama.cpp & CUDA configuration
- [Testing & QA Guide](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/development/testing.md) — Running test suites, isolation rules & patterns

---

## High-Level Architecture

```text
                         JARVIS
                            |
          +-----------------+-----------------+
          |                 |                 |
       KNOWLEDGE          CONTEXT             AI
          |                 |                 |
     +----+----+            |          +------+------+
     |         |             |          |             |
  Memory    Evidence         |      AI Service     Providers
     |         |             |          |             |
  Formation  Retrieval       |      +---+---+         |
     |         |             |      |       |         |
     +----+----+             |    Local   OpenAI     ...
          |                  |
          +--------+---------+
                   |
             ContextPackage
                   |
                AIRequest
                   |
              AI Provider
                   |
              AIResponse
```