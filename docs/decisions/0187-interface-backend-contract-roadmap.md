# Decision 187 — M25 Interface Backend Contract and Roadmap

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Purpose
M25 begins the interface layer from the backend inward.

The first boundary is not a GUI. It is a provider-neutral interface backend contract that accepts typed interface requests, routes them to an injected orchestration capability, and returns typed interface responses without redefining JARVIS authority semantics.

## M25 roadmap

```text
M25.1  Interface Backend Contract          ← current
M25.2  Self-Improvement Orchestration
M25.3  Runtime Event / Activity Stream
M25.4  Interface State / Session Model
M25.5  Interface Adapter Boundary
M25.6  Interface Surface                     ← UI / UX
       ↺ iterate from real usage
```

The roadmap is intentionally small. M25 builds the backend contract and orchestration substrate first; the visual/interface surface is downstream of those contracts.

## M25.1 contract

- Accepts a canonical `InterfaceRequest` envelope.
- Requires explicit request identity, session identity, actor identity, and typed operation.
- Freezes request payloads recursively.
- Routes requests only through an injected `InterfaceOrchestrationPort`.
- Produces a canonical `InterfaceResponse` envelope.
- Preserves request identity and operation identity across the response.
- Freezes response payloads recursively.
- Rejects malformed request envelopes before orchestration dispatch.
- Does not itself grant authorization, execute capabilities, mutate state, persist state, establish truth, or establish certainty.
- Interface/provider choices cannot redefine M24 artifact semantics.

## Boundary invariant

```text
Interface Backend ≠ Authority
Interface Backend ≠ Executor
Interface Backend ≠ Persistence
Interface Backend ≠ AI Provider
Interface Backend ≠ M24 Decision
Interface Backend ≠ M24 Application
Interface Backend ≠ M24 Verification
```

The backend is an adapter/transport seam. Authority remains in the existing deterministic boundaries.

## M25 architectural direction

```text
Interface Surface
      ↓
Interface Adapter
      ↓
Interface Backend                 ← M25
      ↓
Orchestration Port
      ↓
M24 Self-Improvement Lifecycle
      ↓
External Capabilities / Runtime
```

The same backend contract should be consumable by a future GUI, CLI, HTTP API, local API, or other interface without changing the underlying JARVIS semantics.

## Verification
Focused verification must cover exact request/response types, required metadata, operation typing, recursive immutability, response identity preservation, malformed-request rejection, injected-port routing, and authority/execution boundary walls.
