# JARVIS Architecture Overview

## 1. Purpose

JARVIS is designed as a persistent personal AI system rather than a single AI model or chatbot wrapper.

The system separates:

- knowledge
- context
- intelligence
- tools
- orchestration

This allows JARVIS to evolve without becoming dependent on a particular AI provider, model, storage engine, or interface.

---

## 2. Core Principle

The central architectural principle is:

> JARVIS is the system. AI is a capability.

An AI model does not own JARVIS memory, tools, databases, or system privileges.

JARVIS controls those systems and provides the model with the context required for a task.

---

## 3. Major Subsystems

```text
src/
|
+-- core/
|   |
|   +-- jarvis.py
|   +-- models.py
|
+-- memory/
|   |
|   +-- memory_store.py
|   +-- evidence_store.py
|   +-- memory_retrieval.py
|
+-- context/
|   |
|   +-- models.py
|   +-- context_builder.py
|
+-- ai/
|   |
|   +-- models.py
|   +-- provider.py
|   +-- service.py
|   +-- errors.py
|   |
|   +-- providers/
|       |
|       +-- local_provider.py
|       +-- ...
|
+-- database.py