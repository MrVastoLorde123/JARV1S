# Decision 013 — Model-Proposed Capability Invocation

## Status
Accepted

## Purpose

Move from explicit tool metadata toward natural-language capability use without giving the model direct execution authority.

## Boundary

The model may propose a JSON object of arguments for a previously selected `ToolDefinition`.

The proposal then passes through `CapabilityInvocationBuilder`, which validates required fields and declared primitive types and materializes a `ToolRequest`.

Only a `ToolRequest` can enter the existing execution path:

`ToolRequest -> PolicyGate -> confirmation (when required) -> ToolService -> handler`

## Rules

- Model output is untrusted data.
- Model output cannot execute a tool.
- The selected capability's schema is the validation source.
- Selection and argument planning remain separate from execution.
- Tool-specific policy and confirmation remain owned by the tool layer.
- A future model-backed structured-output provider can replace the current text-JSON adapter without changing the execution boundary.

## Why

This establishes the Third Hand's critical safety invariant:

> intelligence proposes; deterministic infrastructure validates and authorizes; the executor performs the action.
