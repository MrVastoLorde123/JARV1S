# Decision 068 — M11.2 Session / Conversation Runtime

## Status

IN PROGRESS

## Decision

M11.2 adds a bounded provider-neutral session runtime above M11.1's interface transport boundary. Sessions preserve conversational continuity, request identity, ordering, and request/response correlation without interpreting intent or granting authority.

## Boundary

```text
InterfaceRequest
      ↓
SessionRuntime
      ↓
ConversationSession
      ↓
ConversationTurn
      ↓
InterfaceResponse
      ↓
Future JARVIS processing
```

## Guarantees

- Session identity is explicit and bounded.
- Conversation history is immutable and ordered.
- Each request identity is unique within a session.
- Responses must correlate to the latest pending request.
- Sessions impose an explicit maximum turn bound.
- Session state can be replaced immutably in a provider-neutral `SessionStore`.
- A request without a session identifier can be bound to the active session by the runtime.

## Semantic walls

```text
Session ≠ Intent
Conversation ≠ Truth
Continuity ≠ Authority
History ≠ Authorization
Correlation ≠ Execution
Session State ≠ Policy
Interface ≠ JARVIS
```

## Non-goals

- no intent interpretation
- no authority mutation
- no authorization
- no execution
- no policy mutation
- no automatic persistence provider
- no unbounded conversation history
- no inference that prior conversation grants future permission

## Invariant

A session records what passed through an interface. It does not decide what JARVIS believes, what JARVIS may do, or what JARVIS is authorized to execute.
