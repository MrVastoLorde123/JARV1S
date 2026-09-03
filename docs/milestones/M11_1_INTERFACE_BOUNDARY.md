# M11.1 — Interface Boundary

**Status: IN PROGRESS**

## Goal

Establish a stable, provider-neutral boundary between human/system interface surfaces and JARVIS itself.

## Implemented design

- Immutable `InterfaceRequest` transport envelope.
- Immutable `InterfaceResponse` output envelope.
- Explicit `InterfaceChannel` values for TEXT, VOICE, UI, API, and OTHER.
- Optional bounded session identity.
- Provider-neutral metadata.
- Interface boundary packages traffic without interpreting intent or creating authority.
- All interface surfaces converge on the same JARVIS request boundary.

## Core invariants

```text
Interface ≠ JARVIS Identity
Interface ≠ Intent Interpretation
Channel ≠ Authority
Input ≠ Authorization
Response ≠ Execution
Transport ≠ Policy
Presentation ≠ Truth
Interface Provider ≠ Intelligence Provider
```

## Flow

```text
Voice / Text / UI / API
          ↓
  InterfaceRequest
          ↓
       JARVIS
          ↓
  InterfaceResponse
```

## Verification target

Focused M11.1 tests must cover immutability, normalization, channel convergence, empty-input rejection, provider-neutral metadata, request correlation, deterministic serialization, and explicit denial of authority/execution semantics.
