# JARVIS M28 Interface

The M28 interface is intentionally minimal and truthful. It renders backend-owned world observation and provides one browser command surface into the canonical `JARVISRuntime`.

## Live surfaces

```text
JARVIS
├── World observation      GET /api/world/observation
└── Command input          POST /api/command
```

The interface does not fabricate projects, models, device telemetry, agent work, tool execution, or authority. Capabilities that are not currently exposed are shown explicitly as unavailable or unverified.

## Development

```powershell
cd ui
npm install
npm run dev
```

The Vite development server runs on port `5173`. World observation is proxied to the local JARVIS world host on `8765`; browser commands are proxied to the canonical command transport on `8766`.

The local JARVIS process enables the command transport automatically whenever `JARVIS_WORLD_HTTP=1`, unless `JARVIS_COMMAND_HTTP` is explicitly set to `0`.
