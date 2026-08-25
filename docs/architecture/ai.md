# JARVIS AI Subsystem Architecture

## 1. Purpose

The AI Subsystem provides intelligence and text generation capabilities to JARVIS without becoming JARVIS itself.

> **Core Philosophy:**  
> *"JARVIS is the system. AI is a capability."*

An AI model does not own JARVIS memory, databases, tools, or system privileges.  
JARVIS orchestrates data, retrieves memory, enforces context boundaries, and presents the intelligence provider with a provider-neutral request.

---

## 2. Component Hierarchy

```text
                                  JARVIS Core
                               (src/core/jarvis.py)
                                       │
                                       ▼
                                   AIService
                              (src/ai/service.py)
                                       │
                +----------------------+----------------------+
                │                                             │
      AIProvider (Contract)                         AICapabilities
      (src/ai/provider.py)                        (src/ai/models.py)
                │                                             │
      +---------+---------+                         +---------+---------+
      │                   │                         │                   │
LocalProvider      OpenAIProvider             text_generation       streaming
(llama.cpp)           (Future)                structured_output    tool_calling
```

---

## 3. Data Contracts

- **`AIRequest`** ([`src/ai/models.py`](file:///c:/Users/jeoop/PycharmProjects/JARV1S/src/ai/models.py)):
  Provider-neutral payload containing:
  - `task` (str): The primary user query or task instruction.
  - `context` (`ContextPackage`): Bounded, provider-neutral context prepared by Context Builder.
  - `generation_options` (dict): Optional sampling parameters (temperature, max tokens, etc.).

- **`AIResponse`** ([`src/ai/models.py`](file:///c:/Users/jeoop/PycharmProjects/JARV1S/src/ai/models.py)):
  Provider-neutral payload returned to JARVIS containing:
  - `content` (Any): Text response or structured output.
  - `provider` (str): Name of the provider that handled the request (e.g. `"local"`).
  - `model` (str): Exact model identifier used (e.g. `"qwen3-4b-local"`).
  - `usage` (`AIUsage`): Token consumption stats (input, output, total).

---

## 4. Provider Orchestration (`AIService`)

`AIService` maintains a registry of available `AIProvider` instances:
- Dynamic provider registration (`register_provider()`).
- Default provider selection (`set_default_provider()`).
- Capability checking (`_check_capabilities()`) to verify required capabilities (e.g. `streaming`, `tool_calling`) before execution.
- Task execution dispatch (`generate()`).