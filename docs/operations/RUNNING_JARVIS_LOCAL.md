# Running JARVIS Locally

This is the operational guide for starting the local JARVIS runtime with `llama-server` and a local GGUF model.

> **Current development branch:** use the active milestone feature branch shown by `git branch --show-current`.
>
> The repository's launcher is `scripts/run_jarvis.ps1`.

## 1. Start from the repository root

PowerShell:

```powershell
cd <JARVIS_REPO>
```

Check the branch before doing development work:

```powershell
git branch --show-current
```

For milestone development, switch to the feature branch named by the current milestone. Do **not** use `main` as the working branch for milestone implementation.

## 2. Verify Python

JARVIS currently expects Python to be available on `PATH`.

```powershell
python --version
python -c "import src; print('JARVIS Python environment OK')"
```

## 3. Verify llama-server

The launcher can find `llama-server.exe` from `PATH` or several common locations. An explicit path can always be supplied with `-LlamaServerPath`.

For a machine-specific installation, pass the local executable path without committing that path into the repository:

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "<PATH_TO_LLAMA_SERVER_EXE>"
```

## 4. Put the GGUF model where the launcher can find it

Without `-ModelPath`, the launcher looks for `.gguf` files in:

```text
.\models
%USERPROFILE%\models
```

Exactly one GGUF should be available for automatic selection.

For an explicit model path:

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "<PATH_TO_MODEL_GGUF>"
```

## 5. Normal JARVIS startup

From the repository root:

```powershell
.\scripts\run_jarvis.ps1
```

The launcher performs this sequence:

```text
Repository checks
        ↓
Database bootstrap
        ↓
Find / start llama-server
        ↓
Wait for /v1/models
        ↓
Resolve the active model ID
        ↓
Run AI provider regression tests
        ↓
Run core tests
        ↓
Launch the Human Operating Layer
        ↓
Interactive JARVIS session
```

The launcher binds locally by default:

```text
http://127.0.0.1:8080
```

The local model server is a capability provider. It is not JARVIS itself.

## 6. Interactive Human Operating Layer

The local runner now stays alive for repeated requests instead of sending one hard-coded prompt and exiting.

Example:

```text
JARVIS Human Operating Layer
Commands:
:help          show this help
:session       show the active session ID
:new           start a new session
:quit          end the JARVIS session

You > What do you know about PCVUE?
JARVIS > ...

You > What were we working on?
JARVIS > ...

You > :quit
JARVIS session ended.
```

Normal text is sent through the existing canonical JARVIS runtime. The local control commands stay at the interface layer and do not grant authority or authorization.

## 7. Resume a durable session

To resume an existing session identity, pass a stable session ID:

```powershell
.\scripts\run_jarvis.ps1 -SessionId "my-session-id"
```

The session ID is an identity/continuity handle. It is not an authority token.

## 8. Check llama-server manually

When debugging the model server, check the OpenAI-compatible models endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/v1/models
```

A healthy server should return a model entry.

## 9. Useful launcher options

### Keep llama-server running

```powershell
.\scripts\run_jarvis.ps1 -KeepServer
```

### Skip regression tests

```powershell
.\scripts\run_jarvis.ps1 -SkipTests
```

Use this only when the normal test gate is intentionally being bypassed for local debugging.

### Explicit llama-server executable

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "<PATH_TO_LLAMA_SERVER_EXE>"
```

### Explicit GGUF model

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "<PATH_TO_MODEL_GGUF>"
```

### Explicit durable session

```powershell
.\scripts\run_jarvis.ps1 -SessionId "my-session-id"
```

## 10. What happens when a server is already running?

The launcher first checks whether anything is listening on the configured host/port.

If the port is occupied, it checks `/v1/models` before using that server. It does not blindly assume that every process on the port is llama-server.

If the existing service is healthy, JARVIS reuses it instead of starting another server.

## 11. Environment variables used by JARVIS

Before launching the runtime, the script sets:

```text
JARVIS_LOCAL_BASE_URL=http://127.0.0.1:8080
JARVIS_LOCAL_MODEL=<resolved model id>
JARVIS_SESSION_ID=<optional durable session id>
```

These variables are removed when the launcher exits.

## 12. Server logs

When the launcher starts llama-server itself, stdout and stderr logs are written under:

```text
logs\local\
```

Typical files look like:

```text
llama-server-YYYYMMDD-HHMMSS.out.log
llama-server-YYYYMMDD-HHMMSS.err.log
```

When startup fails, inspect the `.err.log` first.

## 13. Stopping JARVIS

During an interactive JARVIS session, stop the runtime with:

```text
:quit
```

`Ctrl+C` / EOF also exits the operator loop.

When `run_jarvis.ps1` started the model server, it normally stops that server automatically when the JARVIS session ends. With `-KeepServer`, the server is intentionally left running.

## 14. First-time setup checklist

Use this sequence on a fresh clone:

```powershell
cd <JARVIS_REPO>

git fetch --all
git branch --show-current

python --version
python -c "import src; print('JARVIS Python environment OK')"

.\scripts\run_jarvis.ps1
```

If automatic model discovery cannot find exactly one GGUF, use `-ModelPath` explicitly.

If automatic `llama-server.exe` discovery fails, use `-LlamaServerPath` explicitly.

## 15. Mental model

The local runtime is:

```text
YOU
  ↓
Human Operating Layer
  ↓
JARVISRuntime
  ↓
OpenAI-compatible local API
  ↓
llama-server
  ↓
Local model
```

JARVIS owns the runtime semantics. The interface is only the human operating surface, and the model is a capability provider.

## 16. Development rule

Before starting a milestone:

```powershell
git branch --show-current
```

Work on the milestone feature branch, run the focused receipt for the slice, then run the relevant regressions. Do not write milestone work directly to `main`.
