# Decision 011 — Natural-Language Capability Realization

## Context

JARVIS can now classify natural-language input, discover registered capabilities, rank candidate capabilities, and produce validated arguments. These pieces are intentionally provider-neutral and do not execute tools.

The remaining gap is composition: a natural-language `TOOL` request must become one concrete, validated `ToolRequest` that can enter the existing task/execution pipeline.

## Decision

Introduce a capability-realization boundary in `src.core` that composes the existing discovery, selection, argument-planning, and invocation components.

The realization boundary is responsible for:

1. accepting the user's natural-language tool intent;
2. obtaining the current read-only capability catalog;
3. selecting the best capability candidate;
4. asking the configured AI service to propose arguments for that capability;
5. validating those arguments against the selected capability definition; and
6. returning an inert `ToolRequest`.

It must never execute a capability.

```text
Natural language
      |
      v
Capability Realization
      |
      +--> Capability Catalog
      |
      +--> Capability Selection
      |
      +--> Argument Planning (AI proposal)
      |
      +--> Invocation Validation
      |
      v
   ToolRequest
      |
      v
(existing Task -> Plan -> Validator -> Policy -> Confirmation -> Executor)
```

## Safety Boundary

Capability realization is planning only. It does not bypass or duplicate policy enforcement.

`ToolRequest` remains inert until it reaches the existing tool execution boundary. Risk classification, confirmation requirements, blocked-tool rules, filesystem constraints, and actual handler invocation remain owned by the tool/policy layers.

The AI model is therefore granted no direct execution authority. It can propose a capability and arguments; JARVIS validates the proposal and the existing safety pipeline remains authoritative.

## Provider and Core Boundaries

The realization service may depend on provider-neutral interfaces only. It must not import concrete tool handlers or embed filesystem/tool-specific knowledge.

`JARVIS` should receive the realization service through dependency injection rather than constructing tool-specific objects inside `jarvis.py`.

## V1 Behavior

For a natural-language tool request:

- no matching capability -> fail cleanly without invocation;
- ambiguous/low-confidence capability selection -> fail cleanly without invocation;
- invalid model output -> fail cleanly without invocation;
- invalid arguments -> fail cleanly without invocation;
- valid proposal -> return a validated `ToolRequest` and allow the existing execution pipeline to decide whether and how it may run.

Explicit commands and ordinary conversation remain on their existing paths.

## Why This Is the Next Milestone

This completes the first real agency loop of the Third Hand:

> understand intent -> determine available ability -> choose an ability -> formulate the action -> hand it to the safety boundary.

It deliberately stops one boundary before execution so that capability selection can mature independently from authorization and side effects.
