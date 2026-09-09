# Decision 0201 — V2 HOME Awareness and MIND Core

**Status:** ACCEPTED IN M27.7 / AWAITING LOCAL VERIFICATION

## Purpose

MIND and HOME have distinct roles in the JARVIS interface and system experience.

## MIND

MIND is a first-class core workspace for JARVIS's internal intellectual state. It is intentionally given its own primary interface space so its purpose is not diluted by also serving as the default landing surface.

MIND is expected to grow into a deeply connected environment containing memory, context, thinking, questions, hypotheses, plans, goals, learning signals, evidence, decisions, relationships, timelines, and other future cognitive structures.

Its navigation may combine enterprise-style hierarchical exploration with relationship visualization. A tree/explorer view provides predictable navigation through large volumes of structured information; a relationship graph exposes how concepts, memories, projects, goals, plans, experiences, skills, capabilities, and other entities connect.

MIND is an understanding environment, not a generic dashboard and not an authority layer. It must expose distinctions between what JARVIS knows, remembers, is considering, is learning, intends, and does not yet know.

## HOME

HOME remains a separate primary space rather than being replaced by MIND. MIND owns the deep internal world; HOME becomes the awareness and orientation layer for the user.

HOME should answer what matters now rather than merely display system metrics. It should surface current focus, meaningful changes, relevant activity, active mental/work state, attention, important relationships or developments, and useful next orientation without pretending to replace MIND.

HOME should feel alive and runtime-derived. It should be a window into the state of the larger JARVIS system, not a conventional analytics dashboard.

## Relationship

The intended distinction is:

- **MIND = internal world / understanding**
- **HOME = what matters now / orientation**
- **CHAT = interaction**
- **WORK = doing**
- **CAPABILITIES = what JARVIS can use**
- **SELF = understanding JARVIS itself**

HOME may summarize or reference information from MIND, WORK, CAPABILITIES, and other surfaces, but it must not absorb their purposes.

## Architectural invariants

- MIND remains a dedicated first-class interface space.
- HOME remains separate from MIND and serves awareness/orientation.
- MIND data relationships are navigational and semantic; they do not grant execution authority.
- HOME presentation does not redefine truth, certainty, authorization, or orchestration semantics.
- The UI remains downstream of the JARVIS Gateway and core authority boundaries.
- Future MIND expansion must preserve the existing provenance, evidence, authority, and execution boundaries.
