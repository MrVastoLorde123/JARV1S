# Running JARVIS Locally

This is the operational guide for starting the local JARVIS runtime with `llama-server` and a local GGUF model.

> **Current development branch:** `feature/m16-7-self-development-integration`
>
> The repository's launcher is `scripts/run_jarvis.ps1`.

## 1. Start from the repository root

PowerShell:

```powershell
cd C:\Users\jeoop\PycharmProjects\JARV1S
```

Check the branch before doing development work:

```powershell
git branch --show-current
```

For the current development state, switch to the M16 integration branch:

```powershell
git fetch --all
git checkout feature/m16-7-self-development-integration
git pull origin feature/m16-7-self-development-integration
```

Do **not** use `main` as the working branch for milestone development.

## 2. Verify Python

JARVIS currently expects Python to be available on `PATH`.

```powershell
python --version
python -c "import src; print('JARVIS Python environment OK')"
```

The import check should print:

```text
JARVIS Python environment OK
```

## 3. Verify llama-server

The launcher can find `llama-server.exe` from `PATH` or several common locations. An explicit path can always be supplied with `-LlamaServerPath`.

The locally installed executable used during setup was:

```text
C:\Users\jeoop\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe
```

Check whether PowerShell can find it:

```powershell
Get-Command llama-server.exe -ErrorAction SilentlyContinue
```

If it is not on `PATH`, pass the full path when launching JARVIS:

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "C:\path\to\llama-server.exe"
```

## 4. Put the GGUF model where the launcher can find it

Without `-ModelPath`, the launcher looks for `.gguf` files in:

```text
.\models
%USERPROFILE%\models
```

Exactly one GGUF should be available for automatic selection.

The local model used during setup was Qwen3 4B GGUF, quantized as `Q4_K_M`.

For an explicit model path:

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "C:\path\to\model.gguf"
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
Launch JARVIS
        ↓
Stop the server when the session ends
```

The launcher binds locally by default:

```text
http://127.0.0.1:8080
```

This is the intended local setup.

## 6. Check llama-server manually

When debugging the model server, check the OpenAI-compatible models endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/v1/models
```

A healthy server should return a model entry.

To test the server itself without launching JARVIS, run `llama-server.exe` manually and keep the terminal open. This is mainly useful for troubleshooting; the normal workflow should let `run_jarvis.ps1` manage the server.

## 7. Useful launcher options

### Keep llama-server running

```powershell
.\scripts\run_jarvis.ps1 -KeepServer
```

Use this when repeatedly restarting JARVIS without restarting the model server.

### Skip regression tests

```powershell
.\scripts\run_jarvis.ps1 -SkipTests
```

Use this only when the normal test gate is intentionally being bypassed for local debugging.

### Explicit llama-server executable

```powershell
.\scripts\run_jarvis.ps1 -LlamaServerPath "C:\path\to\llama-server.exe"
```

### Explicit GGUF model

```powershell
.\scripts\run_jarvis.ps1 -ModelPath "C:\path\to\model.gguf"
```

### Combine options

```powershell
.\scripts\run_jarvis.ps1 `
    -LlamaServerPath "C:\path\to\llama-server.exe" `
    -ModelPath "C:\path\to\model.gguf" `
    -KeepServer
```

## 8. What happens when a server is already running?

The launcher first checks whether anything is listening on the configured host/port.

If `127.0.0.1:8080` is already occupied, it checks `/v1/models` before using that server. It does not blindly assume that every process on port 8080 is llama-server.

If the existing service is healthy, JARVIS reuses it instead of starting another server.

## 9. Environment variables used by JARVIS

Before launching the runtime, the script sets:

```text
JARVIS_LOCAL_BASE_URL=http://127.0.0.1:8080
JARVIS_LOCAL_MODEL=<resolved model id>
```

These variables are removed when the launcher exits.

## 10. Server logs

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

## 11. Stopping JARVIS

During an interactive JARVIS session, stop the runtime with:

```text
Ctrl+C
```

When `run_jarvis.ps1` started the model server, it normally stops that server automatically when the JARVIS session ends.

When started with `-KeepServer`, the server is intentionally left running.

## 12. First-time setup checklist

Use this sequence on a fresh clone:

```powershell
cd C:\Users\jeoop\PycharmProjects\JARV1S

git fetch --all
git checkout feature/m16-7-self-development-integration
git pull origin feature/m16-7-self-development-integration

python --version
python -c "import src; print('JARVIS Python environment OK')"

.\scripts\run_jarvis.ps1
```

If automatic model discovery cannot find exactly one GGUF, use `-ModelPath` explicitly.

If automatic `llama-server.exe` discovery fails, use `-LlamaServerPath` explicitly.

## 13. Mental model

The local runtime is:

```text
YOU
  ↓
JARVIS runtime
  ↓
OpenAI-compatible local API
  ↓
llama-server
  ↓
Qwen3 4B GGUF
```

JARVIS owns the runtime semantics. `llama-server` is the local model-serving layer, and the model is a capability provider rather than JARVIS itself.

## 14. Development rule

Before starting a milestone:

```powershell
git branch --show-current
```

Work on the milestone feature branch, run the focused receipt for the slice, then run the relevant regressions. Do not write milestone work directly to `main`.

## 15. Current known-good local state

The local environment used for this guide has successfully demonstrated:

- Python imports for JARVIS
- `llama-server.exe` installation
- Qwen3 4B GGUF model availability
- llama-server listening on `127.0.0.1:8080`
- `/v1/models` responding successfully
- local model loading and inference

The launcher itself also performs its own readiness and regression checks before starting the JARVIS runtime.
