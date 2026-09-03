# Decision 068 — M11.3 Interface → JARVIS Request Boundary

## Status

IN PROGRESS

## Decision

M11.3 introduces a provider-neutral `JARVISRequest` envelope and `InterfaceRequestBridge` between the M11 interface/session layer and the JARVIS core.

The bridge preserves request identity, source identity, session identity, channel, content, and metadata. It does not interpret intent, grant authority, authorize execution, mutate policy, or select a provider.

## Architecture

```text
Voice / Text / UI / API
          ↓
InterfaceRequest
          ↓
Session / Conversation
          ↓
InterfaceRequestBridge
          ↓
JARVISRequest
          ↓
JARVIS semantic pipeline
```

## Semantic walls

```text
Interface ≠ JARVIS
Transport ≠ Intent
Intent Interpretation ≠ Authorization
Input ≠ Permission
Request ≠ Execution
Presentation ≠ Truth
Interface ≠ Authority
```

## Non-goals

- no autonomous intent interpretation
- no authority mutation
- no authorization
- no execution
- no capability selection
- no provider selection
- no policy mutation

## Rationale

All human and machine interfaces must converge on one request contract so the underlying JARVIS semantics remain independent of presentation technology. Different interfaces may vary in transport, but they must not create different authority or execution paths.

M11.3 is complete only when the focused request-boundary tests and interface discovery suite are green.
