# Decision 199 — V2 Rich Desktop Interface

Status: IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose

V2 makes the human interface the primary development surface. M25.6 established a safe terminal presentation boundary; this milestone creates the first richer desktop cockpit without moving semantics or authority into the UI.

## Decision

Introduce a standard-library desktop interface built with Tkinter. The desktop surface is a presentation layer over an injected runtime/interface contract.

The surface provides conversation-first response history, a persistent command composer, quick lifecycle actions, live session status, activity visibility, capability visibility, keyboard-friendly submission, clear result states, and clean shutdown.

## Boundary

```text
Human
  ↓
JarvisDesktopInterface
  ↓
Existing InterfaceAdapter / backend
  ↓
Canonical orchestration and authority boundaries
```

The desktop surface never calls tools, policies, authorization services, model providers, persistence, or execution services directly.

## UX direction

The surface is a daily cockpit rather than a developer test console. Normal use should hide internal boundary machinery while keeping system state understandable.

## Explicit non-powers

```text
Desktop Interface ≠ Authority
Desktop Interface ≠ Orchestration
Desktop Interface ≠ Executor
Desktop Interface ≠ Authorization
Desktop Interface ≠ Persistence
Desktop Interface ≠ AI Provider
Desktop Interface ≠ Truth / Certainty
```

## V2 evolution

This becomes the base for natural-language conversation, memory views, task/workflow views, approval prompts, notifications, voice, and richer tool panels. Those features must continue crossing the canonical interface boundary.

## Completion criterion

The milestone is complete when the desktop surface renders through injected existing contracts, submits through the canonical interface path, displays responses/activity/status/capabilities, handles invalid input safely, and passes focused tests plus core regression.
