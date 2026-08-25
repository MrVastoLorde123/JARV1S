# Local AI Provider Guide

## Overview

JARVIS is designed as a persistent, provider-neutral technical companion.

> **Core Distinction:**  
> The local AI model is **an ability** of JARVIS—it is **not JARVIS itself**.  
> JARVIS retains memory, conversation state, context bounds, and system privileges. The local AI model serves as interchangeable intelligence used to process tasks.

---

## Baseline Hardware & Model Configuration

- **Model**: Qwen3-4B Q4_K_M (Quantized GGUF)
- **Runtime**: `llama.cpp` / `llama-server`
- **Backend Acceleration**: CUDA
- **Context Window**: 8,192 tokens
- **Hardware Profile**: NVIDIA GTX 1650 Ti Max-Q, 32 GB RAM

---

## 1. Running the Local Server (`llama.cpp`)

Launch the OpenAI-compatible server endpoint via `llama.cpp`:

```powershell
llama-server.exe `
  --model models/qwen3-4b-instruct-q4_k_m.gguf `
  --host 127.0.0.1 `
  --port 8080 `
  --ctx-size 8192 `
  --n-gpu-layers 33 `
  --alias qwen3-4b-local
```

Verify that the server is running by sending a health ping:

```powershell
curl http://127.0.0.1:8080/v1/models
```

---

## 2. Using Local Provider in JARVIS

The local provider is implemented in [`src/ai/providers/local_provider.py`](file:///c:/Users/jeoop/PycharmProjects/JARV1S/src/ai/providers/local_provider.py).

To execute queries using the local provider, instantiate `LocalProvider` and register it with `AIService`:

```python
from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.core.jarvis import JARVIS

# 1. Initialize Local Provider
provider = LocalProvider(
    base_url="http://127.0.0.1:8080",
    model="qwen3-4b-local",
    timeout=120,
)

# 2. Register with AI Service
ai_service = AIService(default_provider="local")
ai_service.register_provider(provider)

# 3. Create JARVIS Instance (with Memory Formation enabled)
jarvis = JARVIS(
    ai_service=ai_service,
    enable_memory_formation=True,
)

# 4. Interact with JARVIS
response = jarvis.ask("What are my active projects?")
print(response.content)
```

---

## 3. Provider Switching & Standalone Test

You can quickly run end-to-end local inference via:

```powershell
.venv\Scripts\python src/run_local_jarvis.py
```

Because JARVIS is provider-neutral (see [ADR-001](file:///c:/Users/jeoop/PycharmProjects/JARV1S/docs/decisions/001-jarvis-ai-seperation.md)), external providers (OpenAI, Anthropic, Ollama, etc.) can be registered alongside `local` and selected dynamically per task.
