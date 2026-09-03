# Decision 067 — M11.1 Interface Boundary

## Status

IN PROGRESS

## Decision

M11.1 introduces a provider-neutral interaction boundary between external interface surfaces and the JARVIS system.

Interfaces package interaction; they do not define JARVIS semantics.

## Canonical shape

```text
Voice
Text
UI
API
Other Surface
      ↓
InterfaceRequest
      ↓
JARVIS
      ↓
InterfaceResponse
```

All interface types converge on the same request/response boundary rather than creating separate authority or reasoning paths.

## Guarantees

- requests and responses are immutable
- request identity is explicit
- interaction channel is explicit metadata, not authority
- raw content is preserved as content; M11.1 does not interpret intent
- session identity is optional and bounded
- interface metadata remains provider-neutral
- responses correlate to request identity
- serialized interface traffic explicitly denies truth, authority, authorization, execution, and policy mutation semantics

## Semantic walls

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

## Non-goals

- no natural-language intent interpretation
- no command execution
- no authorization
- no policy mutation
- no capability expansion
- no provider-specific AI runtime
- no interface-specific authority model

M11.1 is complete only when focused boundary tests and the relevant repository suite are green.
