# Decision 014 — Natural-Language Request Routing

## Status
In progress

## Purpose

Let JARVIS interpret ordinary natural language as conversation, question, task, or tool-oriented work without weakening explicit command behavior or execution safety.

## Decision

Add a provider-neutral `RequestIntentClassifier` contract and an `AIRequestIntentClassifier` adapter. The classifier returns a small immutable `RequestIntent` value.

`IntelligentRequestRouter` composes the existing deterministic `RequestRouter` with the classifier:

```text
incoming text
    |
    +--> explicit command? --> COMMAND
    |
    v
natural-language classifier
    |
    +--> conversation/question --> conversational path
    |
    +--> task --> TaskRequest(ACTION)
    |
    +--> tool --> TaskRequest(TOOL)
```

The classifier and router never execute tools. Tool-oriented intent only becomes a structured task and must continue through capability selection, invocation validation, plan validation, policy, confirmation, and execution.

## Safety Rules

- Explicit command syntax keeps precedence over model classification.
- Model output is untrusted data and is structurally validated.
- Classification does not imply authorization.
- A `TOOL` classification does not contain direct execution authority.
- Existing deterministic request and command contracts remain valid.
- Provider replacement must not require changes to tool execution boundaries.

## Next Integration

A later JARVIS integration step may inject `IntelligentRequestRouter` into `JARVIS.ask()` so normal natural-language requests can enter the task path. That integration should be tested separately from classification itself.
