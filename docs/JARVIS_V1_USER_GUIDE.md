# JARVIS V1 User Guide

> **Frozen operating baseline:** `feature/ops-operational-jarvis-v1` at commit `88f87f4d2b95c7a8800aed9ae7297180e1eb706d`  
> **Status:** V1 operational baseline / daily-driven freeze  
> **Pull request:** #432 — OPEN / UNMERGED  
>
> This guide describes what the frozen V1 system actually does today. It is an operator manual, not a future-architecture promise.

---

## 1. What JARVIS V1 is

JARVIS is the **Third-Hand + Second-Brain** system.

The model is only one capability inside JARVIS. JARVIS itself is the governed runtime around that model: interface, context, memory, reasoning, planning, capability selection, policy, confirmation, authorization, execution, observation, verification, recovery, learning, and durable operational state.

The V1 loop is:

```text
YOU
 ↓
INTERFACE
 ↓
UNDERSTAND
 ↓
REMEMBER / CONTEXTUALIZE
 ↓
OBSERVE CURRENT STATE
 ↓
REASON
 ↓
FORM GOAL
 ↓
PLAN
 ↓
PROPOSE
 ↓
CAPABILITY SELECTION
 ↓
VALIDATION / POLICY
 ↓
CONFIRMATION (when required)
 ↓
AUTHORIZATION
 ↓
EXECUTION
 ↓
OBSERVATION
 ↓
VERIFICATION (when an admissible verifier exists)
 ↓
RECOVERY / CONTINUATION
 ↓
RESULT
 ↓
OUTCOME / EXPERIENCE
 ↓
LEARNING / ADAPTATION HINTS
 ↓
FUTURE BEHAVIOR
```

The important consequence is:

> You can now **drive JARVIS with real requests instead of only studying its architecture**.

V1 does not mean JARVIS can perform every imaginable real-world action. It means the complete operational machinery exists and is connected. Actual authority and capability remain bounded by what is registered, allowed, confirmed, authorized, executable, and verifiable.

---

# 2. The most important mental model

Think of JARVIS as having three different roles:

### The intelligence

The AI/model can interpret language, reason, generate plans, produce code, summarize information, and propose actions.

### The system

JARVIS owns the lifecycle around the intelligence. It provides memory/context, deterministic boundaries, durable job state, capability access, authorization, execution, verification, recovery, and learning.

### You

You remain the ultimate authority.

The architecture deliberately prevents these substitutions:

```text
Intelligence ≠ Authority
Learning ≠ Authority
Capability ≠ Permission
Planning ≠ Execution
Proposal ≠ Authorization
Authorization ≠ Verification
Execution Result ≠ Verified Effect
Observation ≠ Truth
Verification ≠ Truth
Memory ≠ User Intent
Confidence ≠ Certainty
```

That separation is not a philosophical statement. It is implemented in the runtime and tested as part of the V1 closure work.

---

# 3. What you can do with V1

Daily use falls into five broad modes.

## Mode A — Ask

Use ordinary natural-language requests for questions, explanations, analysis, research tasks, and contextual work.

Example:

```text
What were we working on with PCVue?
```

```text
Explain why the ATS Modbus tester works but our integration does not.
```

```text
Compare these two approaches and tell me what information is still missing before we act.
```

Normal text goes through the canonical JARVIS request path.

---

## Mode B — Give it work

For durable autonomous work, use:

```text
:work <goal>
```

Example:

```text
:work Investigate why the current Modbus integration disagrees with the known-good tester and produce a bounded diagnosis.
```

JARVIS creates a durable autonomous job.

The result includes:

- Job ID
- Goal
- Current status

The work is driven through the same underlying JARVIS processor and agency path instead of a second autonomous architecture.

---

## Mode C — Inspect work

List jobs:

```text
:jobs
```

Inspect one job:

```text
:job <job-id>
```

A job inspection exposes:

- Job ID
- Status
- Goal
- Progress as `steps/max_steps`
- Whether it is waiting
- Result, when present
- Failure reason, when present

Working context is deliberately not dumped through the UI surface.

---

## Mode D — Resume or control a job

Resume a waiting or paused job:

```text
:resume <job-id> confirm
```

or provide structured input:

```text
:resume <job-id> {"key":"value"}
```

Cancel a job:

```text
:cancel <job-id>
```

These commands do not bypass JARVIS policy or capability authority. They operate the durable lifecycle around the existing runtime.

---

## Mode E — Reconcile an ambiguous execution

After a restart or crash, JARVIS may refuse to continue because an external action could have happened and the runtime cannot prove the outcome.

Use:

```text
:reconcile <job-id> {"outcome":"COMPLETED","evidence":"...","result":"..."}
```

or:

```text
:reconcile <job-id> {"outcome":"FAILED","evidence":"...","reason":"..."}
```

Reconciliation is not a replay.

It is an explicit operator statement that closes an unresolved lifecycle state. The reconciliation evidence does not magically become independent external verification.

---

# 4. Starting JARVIS locally

The supported local launcher is:

```powershell
.\scripts\run_jarvis.ps1
```

Run it from the repository root.

## Normal startup sequence

The launcher performs:

```text
Repository checks
    ↓
Database bootstrap
    ↓
Find / start llama-server
    ↓
Wait for /v1/models
    ↓
Resolve active model
    ↓
Run AI-provider regression tests
    ↓
Run core regression suite
    ↓
Launch JARVIS
```

The default local model endpoint is:

```text
http://127.0.0.1:8080
```

The launcher normally starts the local model server when it is not already running.

When it starts the server itself, the server is normally stopped again when the JARVIS session ends. Use `-KeepServer` to intentionally leave it running.

---

# 5. First-time/local setup

From PowerShell:

```powershell
cd <JARVIS_REPO>

git branch --show-current

python --version
python -c "import src; print('JARVIS Python environment OK')"

.\scripts\run_jarvis.ps1
```

Current backend target is Python 3.12.

The repository runtime does not require a third-party Python installation step for the current backend architecture.

---

# 6. Model configuration

The launcher can discover `llama-server.exe` from PATH or common local locations.

Provide an explicit path when needed:

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "C:\path\to\llama-server.exe"
```

For the GGUF model, the launcher looks in:

```text
.\models
%USERPROFILE%\models
```

Automatic selection expects exactly one GGUF.

For an explicit model:

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "C:\path\to\model.gguf"
```

The model is a provider. It is not JARVIS itself.

---

# 7. Persistent data

JARVIS uses `JARVIS_DATA_DIR` as its persistence root.

A reproducible explicit deployment can use:

```powershell
.\scripts\run_jarvis.ps1 -DataDir "C:\JARVIS\data"
```

The canonical SQLite database is created under:

```text
C:\JARVIS\data\processed\jarvis.db
```

When `-DataDir` is omitted:

1. an existing `JARVIS_DATA_DIR` value is respected;
2. otherwise the repository `data` directory is used.

The launcher restores the caller's previous environment when it exits.

---

# 8. Durable sessions

A session ID gives the interface a persistent identity.

Start with an explicit session:

```powershell
.\scripts\run_jarvis.ps1 -SessionId "my-session-id"
```

Inside JARVIS:

```text
:session
```

starts a new visible session identity:

```text
:new
```

The session ID is continuity metadata.

It is **not** an authority token.

Changing a session does not grant new permissions.

---

# 9. Human Operating Layer commands

The operator layer recognizes these commands:

| Command | Purpose |
|---|---|
| `:help` | Show command help |
| `:session` | Show active session ID |
| `:new` | Start a new session |
| `:work <goal>` | Submit durable autonomous work |
| `:jobs` | List persisted autonomous jobs |
| `:job <job-id>` | Inspect one autonomous job |
| `:resume <job-id> confirm` | Resume a job using explicit confirmation |
| `:resume <job-id> {"key":"value"}` | Resume a job with structured input |
| `:reconcile <job-id> {...}` | Resolve an ambiguous execution state |
| `:cancel <job-id>` | Cancel a job |
| `:quit` | End the operator session |
| `:exit` | Alias for `:quit` |

Anything that does not begin with `:` is treated as normal JARVIS content.

Unknown commands do not execute as normal text. They return an unknown-command response and point you to `:help`.

---

# 10. What ":work" actually means

`:work` does not create a free-running unrestricted agent.

It creates a durable bounded job around the existing JARVIS processor.

A job is:

- persistent;
- bounded;
- resumable in defined lifecycle states;
- scheduler-driven;
- observable;
- cancellable;
- subject to the existing JARVIS authority chain.

The default job limit is 32 work cycles.

The continuous runtime can run in the background and uses durable SQLite state plus fenced scheduling/leases.

---

# 11. Autonomous job states

A job can occupy these states:

```text
QUEUED
RUNNING
WAITING_AUTHORIZATION
WAITING_INPUT
WAITING_TOOL
PAUSED
COMPLETED
FAILED
CANCELLED
```

The practical meaning is:

### QUEUED

The goal has been created and persisted, but execution has not yet started.

### RUNNING

JARVIS is actively driving a bounded work cycle.

### WAITING_AUTHORIZATION

JARVIS reached an existing confirmation/authorization boundary.

The autonomous runtime will not invent authority for itself.

### WAITING_INPUT

JARVIS needs more information from you.

### WAITING_TOOL

The current work cannot continue until the required tool-side condition is satisfied.

### PAUSED

Work was intentionally or safely stopped.

A restart can also cause a running job to become paused when runtime ownership is no longer safe to assume.

### COMPLETED

The autonomous cycle reached a completed result.

This means the JARVIS execution path produced a completion result. It does not automatically mean every external-world effect was independently verified.

### FAILED

The bounded autonomous lifecycle exhausted its available path or hit a non-recoverable failure.

### CANCELLED

The job was explicitly cancelled.

---

# 12. Bounded recovery

Autonomous execution has bounded recovery.

The current worker defaults to at most two recovery attempts for processor/execution failures before failing the autonomous job.

A recovery cycle is not permission to repeat an unsafe action blindly.

The runtime explicitly carries recovery context forward and asks the canonical processor to continue from the previous evidence rather than blindly repeat an unchanged failed action when another bounded path is available.

The important rule is:

> Recovery is continuation under the existing authority chain, not a backdoor around it.

---

# 13. Restart behavior

A restart is a first-class lifecycle event.

JARVIS inspects durable jobs when the operational runtime is reconstructed.

A running job whose scheduler ownership is no longer active is not simply assumed safe to continue.

Instead it is paused.

If an execution-attempt marker exists, the job becomes explicitly marked as requiring ambiguous-execution recovery.

The job retains the execution-attempt identity.

JARVIS does not silently replay the operation.

This is the correct behavior for operations where an external effect may have happened immediately before a process failure.

---

# 14. Ambiguous execution: what to do

When you see a recovery-required state like:

```text
AMBIGUOUS_EXECUTION
```

do not press `:resume` and hope.

The correct sequence is:

1. inspect the job;
2. determine what the external system actually shows;
3. reconcile the outcome explicitly;
4. only then continue if appropriate.

Example completed reconciliation:

```text
:reconcile job-123 {"outcome":"COMPLETED","evidence":"The external system shows the record exists with the expected identifier.","result":"Record creation confirmed externally."}
```

Example failed reconciliation:

```text
:reconcile job-123 {"outcome":"FAILED","evidence":"The external system shows no created record after the failed attempt.","reason":"No external record exists; the attempted operation did not take effect."}
```

Reconciliation closes the lifecycle state.

It does not claim that the operator's statement is an independent verifier.

---

# 15. Confirmation and authorization

Some operations cross an explicit confirmation boundary.

When JARVIS asks for confirmation, the safest mental model is:

```text
JARVIS proposed an action
        ↓
policy evaluated it
        ↓
confirmation required
        ↓
you confirm
        ↓
authorization continues
        ↓
execution may proceed
```

Do not interpret a plan, proposal, or model response as authorization.

The V1 system preserves the distinction between:

```text
PROPOSAL
    ≠
CONFIRMATION
    ≠
AUTHORIZATION
    ≠
EXECUTION
```

---

# 16. Verification: the most important V1 distinction

JARVIS now has a dedicated evidence path for external outcomes.

The progression is:

```text
EXECUTED
   ≠
OBSERVED
   ≠
VERIFIED
   ≠
TRUTH
```

## Executed

The registered capability handler reported an execution result.

This is what `ToolResult.success == True` means.

It does not mean the external world has been independently checked.

## Observed

JARVIS obtained typed external observation evidence scoped to the intended target.

## Verified

The observed result has typed verification evidence that passes the live admissibility chain.

For live capability verification that chain now requires:

```text
typed verification
    ↓
provenance
    ↓
admissible source
    ↓
registration-bound source identity
    ↓
independent verifier provider
    ↓
VERIFIED
```

The verifier provider cannot simply be the same concrete capability object that executed the operation.

## Truth

V1 still does not claim that `VERIFIED` means metaphysical truth.

Verification is evidence with governed provenance.

---

# 17. What verification means in daily use

When JARVIS reports:

```text
executed
```

read it as:

> The execution handler reported success.

When it reports:

```text
observed
```

read it as:

> JARVIS obtained an external observation tied to the intended target.

When it reports:

```text
verified
```

read it as:

> The available registered verification mechanism produced admissible evidence that supports the intended outcome.

When verification is unavailable, stale, mismatched, or unadmitted, JARVIS should preserve that uncertainty instead of upgrading it to success.

---

# 18. Why V1 has an independent verifier

A major V1 hardening rule is:

```text
EXECUTOR
   ↓
external effect
   ↓
OBSERVATION
   ↓
INDEPENDENT VERIFIER
   ↓
VERIFIED
```

The executing capability cannot simply say:

> "I did it, therefore I verified it."

A registry-bound verifier identity is attached to the actual registered system configuration.

This is why typed evidence, a claimed source string, and a registered independent provider are separate concepts.

---

# 19. Learning in V1

Operational learning is intentionally subordinate to authority.

The V1 rule is:

> JARVIS may learn how to behave without learning how to authorize itself.

Operationally:

```text
execution result
    ↓
outcome evidence
    ↓
evaluation
    ↓
experience
    ↓
future-behavior guidance
```

For positive operational reinforcement, explicit external verification is required.

An unverified execution success can become review-required rather than automatically becoming a success pattern.

Learning can therefore affect future behavior without changing the set of things JARVIS is allowed to do.

---

# 20. Memory and contextual continuity

JARVIS is not meant to treat every interaction as an isolated prompt.

Persistent conversation and memory can feed working context.

The normal causal path is:

```text
durable conversation / memory
        ↓
working context
        ↓
cognition
        ↓
reasoning / planning
        ↓
agency
```

Autonomous jobs also have durable conversational continuity through their job-derived identity.

That means an autonomous job can continue a multi-cycle objective without requiring a second, competing memory system.

---

# 21. Daily request patterns that work well

## A. Ask for understanding

Prefer:

```text
Explain the Modbus problem we have, using what we already learned, then tell me what evidence is still missing.
```

This asks JARVIS to use context while keeping uncertainty visible.

## B. Ask for investigation

```text
Investigate why the known-good Modbus/JBus tester succeeds while the current integration fails. Do not change anything yet. Give me the evidence trail and the likely boundary where they diverge.
```

This clearly separates investigation from mutation.

## C. Ask for a bounded action

```text
Update the configuration so the known-good register addressing is used. Show me the intended change and run the existing verification path.
```

This gives JARVIS a goal while preserving its proposal/confirmation/execution boundaries.

## D. Give autonomous work

```text
:work Investigate the current PCVue integration issue, preserve what we already know, and stop when you need evidence or authorization that you do not have.
```

The explicit stopping condition is valuable.

## E. Ask for durable follow-through

```text
:work Work through this troubleshooting objective across multiple cycles. Keep the useful findings in the job context, avoid repeating completed work, and tell me exactly what you need from me when blocked.
```

This is the natural V1 long-horizon pattern.

---

# 22. How to write good JARVIS requests

A good request usually contains four things:

### Objective

What are we trying to accomplish?

### Constraints

What must not happen?

### Success condition

How will we know the work is useful or complete?

### Stop/ask condition

When should JARVIS stop and involve you?

A strong request looks like:

```text
Goal:
Diagnose why the ATS integration disagrees with the known-good tester.

Constraints:
Do not modify the controller or network configuration.

Success:
Identify the exact frame/register/addressing difference or state what evidence is still missing.

Stop condition:
Do not guess when the device-side behavior is not supported by evidence.
```

This gives the reasoning system room to work without turning ambiguity into authority.

---

# 23. How to use JARVIS for coding

Coding is one of the clearest demonstrations of the V1 operating model.

A useful progression is:

```text
understand the request
      ↓
inspect repository state
      ↓
form a plan
      ↓
propose edits
      ↓
confirm when required
      ↓
apply exact bounded changes
      ↓
run verification
      ↓
report what changed
```

For repository work, be explicit about:

- the objective;
- the branch;
- files/scope;
- whether mutation is allowed;
- required tests;
- what constitutes success;
- what must remain untouched.

Do not assume a model answer is equivalent to an applied change.

Likewise, do not treat a successful write as verified merely because the write command returned success.

---

# 24. How to use JARVIS for research/discovery

JARVIS can be very useful before any action is taken.

A good research request asks it to:

1. gather observations;
2. identify evidence;
3. distinguish facts from interpretation;
4. identify uncertainty;
5. recommend what evidence would reduce uncertainty.

Example:

```text
Investigate this issue and separate:
- directly observed facts,
- evidence from stored context,
- model reasoning,
- hypotheses,
- missing evidence,
- actions that would require authorization.
```

That request aligns directly with the V1 epistemic walls.

---

# 25. How to use JARVIS for long-horizon work

Use `:work` when the task is naturally multi-step.

Good candidates:

- investigations;
- repository analysis;
- documentation work;
- bounded research;
- multi-stage troubleshooting;
- preparation tasks;
- repeated evidence gathering;
- tasks that can be resumed after interruption.

Avoid treating `:work` as magic permission to perform arbitrary actions.

The job driver is an orchestrator.

The canonical JARVIS path still determines whether a concrete action is available and allowed.

---

# 26. When JARVIS should stop

A healthy V1 JARVIS stopping is a success condition, not a failure.

Expect JARVIS to stop or wait when:

- it lacks a required capability;
- confirmation is required;
- authorization is required;
- required input is missing;
- a tool is blocked;
- execution failed and bounded recovery is exhausted;
- the external result is ambiguous;
- verification evidence is unavailable or not admissible;
- continuing would require guessing.

A system that stops at the correct boundary is safer and more trustworthy than one that pretends uncertainty away.

---

# 27. Using the browser UI

The current browser interface is intentionally minimal.

Its live backend surfaces are:

```text
World observation
GET  /api/world/observation

Command input
POST /api/command
```

The Vite development server runs on:

```text
http://localhost:5173
```

The browser command transport uses local port:

```text
8766
```

The read-only control-plane snapshot uses:

```text
8768
```

World observation is exposed through:

```text
8765
```

The UI is intentionally not allowed to fabricate:

- projects;
- model state;
- agent work;
- device telemetry;
- tool execution;
- authority;
- verification.

It displays backend-owned observations.

---

# 28. Starting the browser interface for development

From the repository:

```powershell
cd ui
npm install
npm run dev
```

The development server runs on port 5173.

The local JARVIS process enables the browser command transport when the world HTTP surface is enabled, unless command HTTP is explicitly disabled.

The browser is therefore another interface into the same canonical JARVIS runtime, not a second brain.

---

# 29. Control plane / cockpit

The control plane is observational.

It can project:

- runtime availability;
- task state;
- agents;
- approvals;
- available tools;
- local model/provider state;
- blockers;
- verification state;
- autonomous jobs;
- recent runtime events.

It does not grant authority.

The snapshot explicitly treats these as observational state, not permissions.

---

# 30. Understanding the autonomous job display

The cockpit may show:

```text
job_id
goal
status
step_count
max_steps
waiting_reason
result
failure_reason
resumable
terminal
recovery_required
unresolved_execution_attempt_id
external_effect_verified
reconciliation_source
```

Some fields are deliberately hard-coded to false in the projection:

```text
authority_granted = false
authorization_granted = false
execution_requested = false
```

That is intentional.

The UI should report state, not manufacture power.

---

# 31. Troubleshooting startup

## JARVIS cannot find llama-server

Pass:

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "C:\full\path\llama-server.exe"
```

## JARVIS cannot find a GGUF

Pass:

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "C:\full\path\model.gguf"
```

## Port 8080 is already occupied

JARVIS checks the existing process through:

```text
/v1/models
```

If the service is healthy and exposes a usable model, JARVIS can reuse it.

If the port is occupied by something else, startup fails rather than silently attaching to an unrelated service.

## Model ID mismatch

When exactly one model is exposed, the launcher can use that model even when the requested alias differs.

When multiple models are exposed, specify the intended model alias explicitly.

---

# 32. Troubleshooting autonomous jobs

Start with:

```text
:jobs
```

Then:

```text
:job <job-id>
```

Interpret the status first.

### WAITING_AUTHORIZATION

The job is waiting for an existing authorization/confirmation boundary.

### WAITING_INPUT

Give the missing information:

```text
:resume <job-id> {"missing_key":"value"}
```

### PAUSED

Determine why it is paused before resuming.

### AMBIGUOUS_EXECUTION

Reconcile first.

Do not blindly resume.

### FAILED

Inspect the failure reason. Bounded recovery may already have been exhausted.

### COMPLETED

Treat the result as the runtime's completion result. Review verification status when an external effect matters.

---

# 33. When to use ":new"

Use:

```text
:new
```

when you intentionally want a fresh conversational session identity.

Do not use it as a reset button for the whole system.

A new session does not delete durable memory, autonomous jobs, or registered capability configuration.

It changes the current interface continuity identity.

---

# 34. What ":quit" does

```text
:quit
```

ends the current Human Operating Layer session.

It does not imply:

- delete memory;
- cancel every autonomous job;
- revoke all authorization;
- destroy the database;
- erase work.

When the launcher started llama-server itself, the launcher normally stops that model server after the session ends unless `-KeepServer` was supplied.

---

# 35. What JARVIS V1 does not promise

V1 is operational, but it is not omnipotent.

Do not assume that JARVIS can:

- access a system that has no registered capability path;
- authorize itself;
- manufacture permissions from reasoning;
- turn a model response into truth;
- convert an execution result into independent verification;
- silently replay ambiguous external actions;
- verify arbitrary reality without an admissible verification source;
- change its own authority because it learned something;
- bypass confirmation because a task feels obvious.

These limits are part of the architecture.

---

# 36. V1 operating doctrine

Use these as the core rules when driving JARVIS:

### Rule 1 — Ask for outcomes, not internal theatrics

You care about the work.

### Rule 2 — Separate investigation from mutation

Tell JARVIS whether it is allowed to change something.

### Rule 3 — State constraints explicitly

A precise boundary gives JARVIS useful freedom inside the correct box.

### Rule 4 — Ask for evidence

Especially when the result matters.

### Rule 5 — Treat "completed" and "verified" differently

They are not synonyms.

### Rule 6 — When JARVIS stops, inspect the reason

Stopping may be the correct safety behavior.

### Rule 7 — Let durable jobs handle durable work

Use `:work` instead of trying to maintain long tasks entirely through one conversation turn.

### Rule 8 — Reconcile ambiguous actions before resuming

Never guess whether an external effect happened.

---

# 37. Recommended daily workflow

A practical day-to-day pattern is:

```text
START
  ↓
check JARVIS runtime
  ↓
ask / inspect context
  ↓
choose:
  ├─ normal request
  └─ :work <goal>
  ↓
let JARVIS reason / act within bounds
  ↓
inspect result
  ↓
check verification when external effects matter
  ↓
resolve blockers
  ↓
resume / confirm / reconcile as necessary
  ↓
capture useful outcome
  ↓
move to next task
```

For multi-hour work, keep the job identity and outcome trail intact rather than restarting the reasoning from scratch every time.

---

# 38. The operator's vocabulary

These words have specific meanings in JARVIS.

| Term | Meaning |
|---|---|
| Request | What enters the JARVIS interface |
| Goal | The objective a normal or autonomous task is trying to accomplish |
| Plan | Proposed sequence of bounded work |
| Proposal | Candidate action/request before authority is established |
| Capability | A registered mechanism capable of doing a class of work |
| Policy | Deterministic constraints around what may proceed |
| Confirmation | Human approval required by the operation |
| Authorization | The deterministic permission boundary for the operation |
| Execution | Invocation of a registered capability |
| Observation | Typed external evidence about what is seen |
| Verification | Admissible evidence that supports an intended external outcome |
| Outcome | Aggregated execution/observation/verification state |
| Experience | Durable evidence that can feed bounded learning |
| Learning | Changes to future advisory behavior |
| Job | Durable long-running autonomous lifecycle |
| Reconciliation | Operator resolution of an ambiguous in-flight execution |
| Session | Human-facing continuity identity |

---

# 39. The deepest V1 rule

The most important thing to understand when studying JARVIS is this:

> **JARVIS is designed to become more capable without becoming self-authorizing.**

That is why the architecture intentionally has many boundaries.

More intelligence should make JARVIS better at understanding and solving problems.

More memory should make it more context-aware.

More learning should make future behavior more useful.

More capabilities should make it able to do more.

More verification should make external outcomes better evidenced.

None of those things, alone, should become permission.

---

# 40. V1 freeze statement

This document treats commit:

```text
88f87f4d2b95c7a8800aed9ae7297180e1eb706d
```

as the **V1 operational baseline**.

The freeze means:

- the operational loop exists;
- the daily operator surface exists;
- durable autonomous work exists;
- restart/recovery semantics exist;
- learning continuity exists;
- outcome verification is explicitly modeled;
- verifier provenance is bound;
- executor/verifier separation is enforced;
- UI/control surfaces are observational;
- the system is ready to be driven by real work.

Future architecture should not reopen foundational V1 boundaries merely because another abstract feature would be interesting.

The preferred post-freeze loop is:

```text
USE
 ↓
OBSERVE
 ↓
FIND REAL LIMIT
 ↓
DEFINE NEXT BOUNDARY
 ↓
IMPLEMENT
 ↓
VERIFY
 ↓
USE BETTER
```

---

# 41. Quick command card

Keep this section handy:

```text
:help
:session
:new

:work <goal>
:jobs
:job <job-id>

:resume <job-id> confirm
:resume <job-id> {"key":"value"}

:reconcile <job-id> {"outcome":"COMPLETED","evidence":"...","result":"..."}
:reconcile <job-id> {"outcome":"FAILED","evidence":"...","reason":"..."}

:cancel <job-id>

:quit
```

---

# 42. One sentence to remember

**Drive JARVIS toward outcomes, demand evidence when outcomes matter, and never confuse intelligence, execution, verification, or learning with authority.**
