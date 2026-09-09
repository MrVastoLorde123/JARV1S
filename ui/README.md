# JARVIS Interface

The V2 interface is a separate React + TypeScript presentation domain.

## Product map

```text
JARVIS
├── HOME            living system state + conversation
├── WORK            active and waiting work
├── MIND            memory + knowledge
├── CAPABILITIES    tools + models + integrations
└── SELF            architecture + health + learning
```

The UI is not a Python client. It consumes the `JarvisGateway` contract and stable presentation models. The transport can evolve from local development to HTTP + SSE/WebSocket without changing the core presentation model.

## Development

```powershell
cd ui
npm install
npm run dev
```

The current shell intentionally uses a local snapshot so the visual language can be exercised before live gateway transport is attached.
