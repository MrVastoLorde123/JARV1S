# M11.2 — Session / Conversation Runtime

**Status: IN PROGRESS**

## Goal

Provide bounded conversational continuity above the M11.1 interface boundary without allowing session history to become authority, authorization, or implicit consent.

## Implemented

- Immutable `ConversationTurn` request/response pair.
- Immutable bounded `ConversationSession`.
- Explicit request identity uniqueness within a session.
- Strict response correlation to the latest pending request.
- Explicit pending-request state.
- Bounded turn history via `max_turns`.
- Immutable conflict-aware `SessionStore`.
- Provider-neutral session serialization.

## Core invariants

```text
Session ≠ Intent
Conversation ≠ Truth
Continuity ≠ Authority
History ≠ Authorization
Correlation ≠ Execution
Session State ≠ Policy
Interface ≠ JARVIS
Prior Interaction ≠ Future Consent
```

## Flow

```text
InterfaceRequest
      ↓
SessionRuntime
      ↓
ConversationSession
      ↓
Pending / Completed Turn
      ↓
InterfaceResponse
      ↓
JARVIS Processing
```

## Verification target

Focused tests cover session identity, bounds, request binding, response correlation, immutability, store conflicts, pending state, deterministic serialization, and explicit denial of authority/execution semantics.
