# M11 — Interface / Experience

**Status: VERIFIED / COMPLETE**

M11 establishes the human/system-facing interface layer without making any interface, session, event stream, modality, or human interaction surface an authority over JARVIS.

## Verified milestones

```text
M11.1 — Interface Boundary
12/12 focused ✅

M11.2 — Session / Conversation Runtime
16/16 focused ✅

M11.3 — Intent → JARVIS Request
12/12 focused ✅

M11.4 — Streaming / Event Experience
17/17 focused ✅
57/57 interface discovery ✅

M11.5 — Multi-Modal Interface
15/15 focused ✅
72/72 interface discovery ✅

M11.6 — Human-in-the-Loop Experience
19/19 focused ✅
91/91 interface discovery ✅

M11.7 — Interface Reliability / Recovery
20/20 focused ✅
111/111 interface discovery ✅
```

## Architecture

```text
Voice / Text / UI / API / Other Surface
                ↓
        Interface Boundary
                ↓
      Session / Conversation
                ↓
          Request Bridge
                ↓
       Provider-neutral Request
                ↓
         JARVIS Core
                ↓
  Intelligence / Agency / Authority
```

M11.4 adds bounded streaming events. M11.5 adds modality descriptors and multi-modal envelopes. M11.6 adds explicit human decision exchange. M11.7 adds interface continuity/recovery state.

## Semantic walls

```text
Interface ≠ JARVIS
Channel ≠ Authority
Session ≠ Authority
Event ≠ Intent
Event ≠ Truth
Modality ≠ Intent
Media ≠ Truth
Human Input ≠ Authorization
Selection ≠ Approval
Approval ≠ Authorization
Recovery ≠ Authorization
Retry ≠ Permission
Resume ≠ Permission
Replay ≠ Permission
Presentation ≠ Authority
Provider ≠ JARVIS
```

The completed M11 layer is a client-facing boundary around JARVIS, not a replacement for the core semantic and authority architecture established by M7–M10.
