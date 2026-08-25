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

## Architecture

At a high level:

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
     +----+----+             |      +---+---+         |
          |                  |      |       |         |
      Retrieval              |    Local   OpenAI     ...
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