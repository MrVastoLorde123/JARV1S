# JARVIS MASTER CONTEXT

> Canonical cross-chat continuity document for the JARVIS project.
>
> This file exists so development can continue across chats without depending on conversation history.
>
> **Source of truth rule:** When a future chat needs project context, read this file first, then inspect the current branch/repository state. Repository code and tests override stale statements here when they conflict.

## 1. Identity

JARVIS is the user's personal intelligence and agency system: **Third Hand + Second Brain**.

It is not being designed primarily as a product to sell. It is a personal system intended to help the user create products and innovations, turn thoughts into words and words into the future, and eventually understand intent so well that explicit instructions become less necessary.

Core long-term loop:

`User → JARVIS understands → remembers → reasons → acts → observes → evaluates → improves → User becomes more capable`

Two complementary halves:

- **Third Hand (M1–M8):** action, execution, automation, inspection, modification, verification.
- **Second Brain (M9–M16):** memory, relationships, persistent projects, self-evaluation, initiative, compounding knowledge/context.

## 2. Non-Negotiable Architecture Principles

### Everything is a capability/plugin

Filesystem is not special. Future capabilities may include GitHub, browser, shell, documents, databases, Home Assistant, PCVUE, research, automation, and other integrations.

A new capability should plug into existing contracts rather than require unrelated changes throughout JARVIS core.

### JARVIS core orchestrates; capabilities implement

Avoid turning `src/core/jarvis.py` into a dependency hub or capability-specific switchboard.

JARVIS should depend on small, stable contracts. Concrete capability implementations belong behind those contracts.

### Model proposes; JARVIS verifies and executes

The AI/model may eventually interpret intent, choose capabilities, construct proposed arguments, and create plans.

It must **not** directly execute arbitrary code or bypass:

`validation → policy → confirmation (when required) → executor → capability`

### Safety is structural

Safety must not depend solely on prompts. Tool risk, workspace boundaries, validation, confirmation, execution authorization, and plan integrity are enforced by code-level boundaries.

### Local-first

JARVIS should remain useful with local models and should not make its core dependent on a single paid/cloud provider. Local-model options considered previously include Qwen/Phi-class models.

### Scraping and automation are backbone capabilities

JARVIS should eventually gather information, operate systems, and automate workflows rather than remain only conversational.

### Controlled self-development

JARVIS should eventually be able to work on itself, but through the same guarded capability system:

`inspect → reason → plan → modify → test → observe → correct → verify`

This is controlled self-improvement, not unrestricted self-modification.

## 3. Repository

GitHub:

`https://github.com/MrVastoLorde123/JARV1S.git`

The real local project directory is:

`C:\Users\jeoop\PycharmProjects\JARV1S`

Earlier duplicate/mock-directory confusion was a workflow mistake and is considered resolved. Do not resurrect that issue without new evidence.

## 4. Current Development State

Current active branch for this milestone:

`feature/capability-selection`

The branch is configured to track:

`origin/feature/capability-selection`

### Last verified local test state

Full regression suite:

`601 tests in 4.950s — OK`

Important prior checkpoints:

- Workspace cohesion freeze: **568 tests — OK**
- Tool capability bridge: **585 tests — OK**
- Capability catalog/selection: **601 tests — OK**

The user reports they do not manually edit the JARVIS source during these guided sessions and watches/examines the changes. Treat unexplained working-tree changes as pre-existing until established otherwise.

Known local working-tree modification that was preserved intentionally:

`src/tools/tests/test_search_files_handler.py`

Do not discard or overwrite this modification blindly.

## 5. Completed Foundation

The following architectural pieces already exist and have passing tests:

- AI provider abstraction and service
- memory system and memory formation
- conversation state
- persistent conversation storage
- context construction
- command parser/registry/service
- request routing
- task models
- execution planner
- execution plan model
- plan validator
- execution policy
- execution confirmation and cancellation
- plan executor
- tool models
- tool registry
- tool service
- tool policy gate
- workspace capability
- filesystem safety boundary
- capability catalog
- capability selection
- core-to-tool execution bridge
- JARVIS-to-tool capability injection

## 6. Workspace Capability — FROZEN

Workspace subsystem is considered architecturally approved/frozen.

Capabilities:

- `read_file`
- `list_directory`
- `search_files`
- `write_file`

Shared `Workspace` behavior covers:

- path resolution
- workspace confinement
- workspace-relative POSIX reporting
- traversal rules
- hidden-entry behavior
- symlink handling
- filesystem-error normalization
- limits

Risk boundary:

- read/list/search are low-risk and read-only
- `write_file` is high-risk and confirmation-gated

Workspace composition has been tested as one coherent capability surface:

`discover → inspect → search → modify`

The workspace layer should not receive feature creep unless a real architectural need appears.

## 7. Tool Capability Bridge — COMPLETED

Core defines the minimal abstraction needed to invoke tools safely:

- `ToolInvoker`
- `ToolCapabilityGateway`
- `ToolPlanStepHandler`

JARVIS receives the tool-facing capability boundary via dependency injection instead of constructing concrete tool infrastructure inside `jarvis.py`.

The core execution policy does not duplicate concrete tool risk. The tool-layer `PolicyGate` owns capability-specific policy/confirmation.

Execution flow:

`JARVIS → TaskRequest → ExecutionPlanner → PlanValidator → ExecutionPolicy → PlanExecutor → ToolPlanStepHandler → ToolInvoker → PolicyGate → ToolService → ToolHandler`

Successful tool output is surfaced back through the JARVIS execution response.

## 8. Capability Catalog + Selection — CURRENT MILESTONE

Current structural pieces:

- `CapabilityCatalog`: read-only deterministic snapshot of available tool definitions
- `CapabilitySelector`: ranks candidate capabilities
- `CapabilitySelectionService`: composes catalog + selector

Selection is intentionally **advisory** and does not invoke tools.

Current conceptual flow:

`natural-language intent → capability candidates → selected/proposed capability → structured invocation → validation → policy → confirmation → execution`

The selector should remain replaceable. A future LLM-backed selector should be able to replace the deterministic selector without changing execution or safety boundaries.

## 9. Current Next Step

Finish M1 by turning intent into a structured, validated invocation.

Target:

`Natural language → intent/task interpretation → capability selection → structured arguments → invocation validation → TaskRequest/ExecutionPlan → policy → confirmation → execution`

A representative first self-work style scenario is:

> “Find the file that defines JARVIS's execution planner.”

Desired behavior:

1. Understand the user's intent.
2. Discover/select `search_files`.
3. Construct safe arguments.
4. Validate the invocation against the capability definition.
5. Execute through the existing policy gate.
6. Observe the result.
7. Optionally inspect/read the relevant file.
8. Return a useful answer.

Do not solve this with hard-coded phrase matching such as `if "execution planner" in text`.

## 10. Roadmap

### GOAL 1 — DRIVEABLE JARVIS / THIRD HAND

#### M1 — Capability Selection

Status: **IN PROGRESS**

Catalog ✅
Selector ✅
Selection service ✅
Tool bridge ✅
Natural-language → structured invocation ⏳

#### M2 — Natural-Language Task Routing

Normal `JARVIS.ask()` should distinguish conversation, question, command, task, and tool-oriented work without weakening deterministic safety.

#### M3 — Multi-Step Agent Execution

Move from one-shot plans toward an observe/act loop:

`goal → plan → step → observe → next step → ... → goal achieved`

#### M4 — Capability Discovery

JARVIS should understand its currently registered capabilities dynamically, not through hard-coded lists.

#### M5 — Persistent Working Context

Combine:

- long-term memory
- conversation state
- current task/goal
- workspace state
- tool observations
- recent history

into coherent working context.

#### M6 — Usable JARVIS Runtime

Move beyond test-driven invocation into a daily-use runtime. CLI/runtime first; polished GUI later.

The runtime should expose conversation, tasks, execution, confirmation, memory, capability status, and useful logs.

#### M7 — Self-Inspection

JARVIS can inspect:

- its own source
- tests
- architecture
- configuration
- runtime state
- capabilities

using the same capability system rather than special bypasses.

#### M8 — Safe Self-Modification + Verification

Driveable threshold.

JARVIS can:

`inspect → identify change → plan modification → confirmation if required → modify → run tests → inspect results → correct/report`

Representative acceptance test:

> “JARVIS, inspect yourself, figure out why X is broken, fix it, run the tests, and tell me what changed.”

### GOAL 2 — “THIS IS JARVIS” / SECOND BRAIN

#### M9 — Goal-Oriented Autonomy

Shift from exact instructions toward outcome-oriented goals.

#### M10 — Persistent Projects

JARVIS understands ongoing projects, tasks, goals, decisions, artifacts, dependencies, experiments, and history across time.

#### M11 — Deep Second-Brain Memory

Memory connects people, projects, ideas, skills, experiences, decisions, preferences, goals, failures, and lessons rather than acting as a simple fact store.

Current memory taxonomy that was previously locked:

`PERSONAL, SKILL, PREFERENCE, PROJECT, GOAL, FACT, WORKFLOW, RELATIONSHIP, EXPERIENCE, OTHER`

#### M12 — Broad Plugin/Capability Ecosystem

Expand the capability ecosystem across tools such as GitHub, browser, shell, documents, research, databases, Home Assistant, PCVUE, automation, etc.

#### M13 — Self-Evaluation

JARVIS evaluates whether a goal was actually achieved, whether assumptions were wrong, what failed, and what should change.

#### M14 — Self-Improvement

Closed improvement loop:

`observe → identify weakness → propose improvement → modify → test → evaluate`

#### M15 — Initiative

JARVIS can notice recurring manual work, bottlenecks, opportunities, and relevant context and bring useful suggestions to the user without silently taking unauthorized actions.

#### M16 — THIS IS JARVIS

JARVIS genuinely feels like a personal intelligence system because it:

- understands the user
- remembers the user and work
- understands projects
- knows its capabilities
- reasons about goals
- acts
- inspects itself
- modifies itself safely
- verifies its work
- helps proactively
- improves over time

## 11. Design Rules for Future Development

Before adding a feature, ask:

**Does this make JARVIS a better partner for the user?**

Avoid building things merely because they are technically interesting.

Prefer existing reliable mechanisms over reinventing infrastructure.

Prefer explicit contracts over magic behavior.

Prefer composition over special cases.

Prefer a small core with extensible capabilities over a monolithic agent.

Never sacrifice safety boundaries for convenience.

Do not optimize for flashy autonomy before the underlying system can explain, test, and verify what it is doing.

## 12. Self-Work Target Architecture

The eventual self-development loop should look like:

`User goal`
`↓`
`Understand`
`↓`
`Discover capabilities`
`↓`
`Inspect current state`
`↓`
`Reason / plan`
`↓`
`Propose actions`
`↓`
`Validate`
`↓`
`Policy / confirmation`
`↓`
`Execute`
`↓`
`Run tests / observe`
`↓`
`Evaluate`
`↓`
`Correct if needed`
`↓`
`Report`

The model is never the final authority over execution.

## 13. Cross-Chat Handoff Format

At the start/end of meaningful milestones, update this file with:

- current branch
- milestone status
- latest verified test count
- important architectural decisions
- unresolved issues
- next concrete milestone

A future chat should be able to begin with:

1. Read `docs/JARVIS_MASTER_CONTEXT.md`.
2. Inspect current branch and git status.
3. Run/inspect the relevant tests.
4. Continue from the stated next milestone.

## 14. Current Snapshot

**Project:** JARVIS

**Identity:** Third Hand + Second Brain

**Current half:** Third Hand

**Current milestone:** M1 Capability Selection

**Current branch:** `feature/capability-selection`

**Latest verified test suite:** `601 tests — OK`

**Workspace:** frozen

**Tool bridge:** complete

**Capability catalog:** complete

**Capability selection:** structurally complete

**Immediate next milestone:** natural-language intent → validated capability invocation

**Long-term defining threshold:** M8 — JARVIS can safely work on itself

**Ultimate target:** M16 — “THIS IS JARVIS”
