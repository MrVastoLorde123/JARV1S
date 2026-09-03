[CmdletBinding()]
param(
    [string]$LlamaServerPath = "",
    [string]$ModelPath = "",
    [string]$BindHost = "127.0.0.1",
    [ValidateRange(1, 65535)]
    [int]$Port = 8080,
    [string]$ModelAlias = "qwen3-4b-local",
    [ValidateRange(256, 131072)]
    [int]$ContextSize = 8192,
    [ValidateRange(5, 600)]
    [int]$StartupTimeoutSeconds = 60,
    [string[]]$AdditionalLlamaArgs = @(),
    [switch]$KeepServer,
    [switch]$SkipGitCheck,
    [switch]$SkipTests,
    [switch]$NoPauseOnError
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Stage {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Fail {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "`nERROR: $Message" -ForegroundColor Red
    if (-not $NoPauseOnError) {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
    exit 1
}

function Test-TcpPort {
    param(
        [Parameter(Mandatory)][string]$TargetHost,
        [Parameter(Mandatory)][int]$TargetPort
    )

    $client = $null
    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $async = $client.BeginConnect($TargetHost, $TargetPort, $null, $null)
        $connected = $async.AsyncWaitHandle.WaitOne(500)
        if ($connected -and $client.Connected) {
            $client.EndConnect($async)
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
    finally {
        if ($null -ne $client) {
            $client.Dispose()
        }
    }
}

function Get-ServerModelIds {
    param([Parameter(Mandatory)][string]$BaseUrl)

    try {
        $result = Invoke-RestMethod `
            -Uri ($BaseUrl + "/v1/models") `
            -Method Get `
            -TimeoutSec 5

        if ($null -eq $result.data) {
            return @()
        }

        return @(
            $result.data |
                ForEach-Object {
                    if ($null -ne $_.id) {
                        [string]$_.id
                    }
                }
        )
    }
    catch {
        return @()
    }
}

function Resolve-ServerModel {
    param(
        [Parameter(Mandatory)][string]$BaseUrl,
        [Parameter(Mandatory)][string]$RequestedModel
    )

    $modelIds = @(Get-ServerModelIds -BaseUrl $BaseUrl)

    if ($modelIds.Count -eq 0) {
        Fail "The local server is reachable, but /v1/models returned no usable model IDs. Check the llama-server logs or configuration."
    }

    Write-Host "Models exposed by server:"
    foreach ($id in $modelIds) {
        Write-Host "  $id"
    }

    if ($modelIds -contains $RequestedModel) {
        return $RequestedModel
    }

    if ($modelIds.Count -eq 1) {
        $selected = $modelIds[0]
        Write-Host "Requested model '$RequestedModel' is not the server's model ID." -ForegroundColor Yellow
        Write-Host "Using the only model exposed by llama-server: $selected" -ForegroundColor Green
        return $selected
    }

    $choices = $modelIds -join ", "
    Fail "Requested model '$RequestedModel' was not found. The server exposes multiple models: $choices. Re-run with -ModelAlias <model-id>."
    return $null
}

function Test-HttpReady {
    param([Parameter(Mandatory)][string]$BaseUrl)

    try {
        $response = Invoke-WebRequest `
            -Uri ($BaseUrl + "/v1/models") `
            -Method Get `
            -TimeoutSec 3 `
            -UseBasicParsing

        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

function Resolve-Executable {
    param([string]$ExplicitPath)

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            Fail "llama-server executable was not found: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $command = Get-Command llama-server.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $commonPaths = @(
        "$env:USERPROFILE\llama.cpp\llama-server.exe",
        "$env:USERPROFILE\llama.cpp\build\bin\Release\llama-server.exe",
        "$env:USERPROFILE\llama.cpp\build\bin\llama-server.exe",
        "C:\llama.cpp\llama-server.exe",
        "C:\llama.cpp\build\bin\Release\llama-server.exe",
        "C:\llama.cpp\build\bin\llama-server.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            return (Resolve-Path -LiteralPath $path).Path
        }
    }

    Fail "Could not find llama-server.exe. Pass -LlamaServerPath <full path>."
    return $null
}

function Resolve-Model {
    param(
        [string]$ExplicitPath,
        [Parameter(Mandatory)][string]$RepoRoot
    )

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            Fail "Model file was not found: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $candidateRoots = @(
        (Join-Path $RepoRoot "models"),
        (Join-Path $env:USERPROFILE "models")
    )

    $models = @()
    foreach ($root in $candidateRoots) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            $models += Get-ChildItem `
                -LiteralPath $root `
                -Filter *.gguf `
                -File `
                -ErrorAction SilentlyContinue
        }
    }

    if ($models.Count -eq 1) {
        return $models[0].FullName
    }

    if ($models.Count -gt 1) {
        $names = ($models | ForEach-Object { $_.FullName }) -join "`n  "
        Fail "Multiple GGUF models were found. Pass -ModelPath explicitly.`n  $names"
    }

    Fail "No GGUF model was found in .\models or $env:USERPROFILE\models. Pass -ModelPath <full path>."
    return $null
}

function Stop-StartedServer {
    param(
        [System.Diagnostics.Process]$Process,
        [bool]$StartedByScript
    )

    if (-not $StartedByScript -or $null -eq $Process) {
        return
    }

    try {
        if (-not $Process.HasExited) {
            Write-Host "Stopping llama-server (PID $($Process.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
            $Process.WaitForExit(3000)
        }
    }
    catch {
        Write-Host "Warning: llama-server may still be running. PID $($Process.Id)" -ForegroundColor Yellow
    }
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot

$serverProcess = $null
$startedByScript = $false
$serverOwnership = "none"
$baseUrl = "http://$BindHost`:$Port"
$effectiveModel = $ModelAlias

try {
    Write-Stage "JARVIS LOCAL LAUNCH"
    Write-Host "Repository : $repoRoot"
    Write-Host "Endpoint   : $baseUrl"
    Write-Host "Requested  : $ModelAlias"

    Write-Stage "Repository checks"
    if (-not $SkipGitCheck) {
        $branch = (git branch --show-current).Trim()
        if ($LASTEXITCODE -ne 0) {
            Fail "Git is not available in this terminal."
        }

        Write-Host "Branch     : $branch"
        if ($branch -notmatch '^feature/m13-1-entity-boundary$') {
            Write-Host "Warning: this launcher is intended for feature/m13-1-entity-boundary." -ForegroundColor Yellow
        }
    }

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Fail "Python was not found on PATH."
    }

    New-Item -ItemType Directory -Force (Join-Path $repoRoot "data\processed") | Out-Null
    New-Item -ItemType Directory -Force (Join-Path $repoRoot "logs\local") | Out-Null

    Write-Stage "Local model server"

    $alreadyListening = Test-TcpPort -TargetHost $BindHost -TargetPort $Port
    if ($alreadyListening) {
        Write-Host "A service is already listening on $baseUrl" -ForegroundColor Green

        if (-not (Test-HttpReady -BaseUrl $baseUrl)) {
            Fail "Port $Port is occupied, but the local OpenAI-compatible /v1/models endpoint is not healthy."
        }

        Write-Host "Existing local model server is HTTP-ready." -ForegroundColor Green
        $effectiveModel = Resolve-ServerModel -BaseUrl $baseUrl -RequestedModel $ModelAlias
        $serverOwnership = "existing"
    }
    else {
        $serverPath = Resolve-Executable -ExplicitPath $LlamaServerPath
        $modelPath = Resolve-Model -ExplicitPath $ModelPath -RepoRoot $repoRoot
        $serverDirectory = Split-Path -Parent $serverPath

        Write-Host "llama-server: $serverPath"
        Write-Host "Model       : $modelPath"

        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $stdoutLog = Join-Path $repoRoot "logs\local\llama-server-$timestamp.out.log"
        $stderrLog = Join-Path $repoRoot "logs\local\llama-server-$timestamp.err.log"

        $arguments = @(
            "--model", $modelPath,
            "--alias", $ModelAlias,
            "--host", $BindHost,
            "--port", $Port,
            "--ctx-size", $ContextSize
        )

        if ($AdditionalLlamaArgs.Count -gt 0) {
            $arguments += $AdditionalLlamaArgs
        }

        Write-Host "Starting llama-server..." -ForegroundColor Green
        Write-Host "Logs       : $stdoutLog"

        $serverProcess = Start-Process `
            -FilePath $serverPath `
            -ArgumentList $arguments `
            -WorkingDirectory $serverDirectory `
            -RedirectStandardOutput $stdoutLog `
            -RedirectStandardError $stderrLog `
            -PassThru

        $startedByScript = $true
        $serverOwnership = "started-by-script"
        Write-Host "llama-server PID: $($serverProcess.Id)"

        $ready = $false
        $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 750

            if ($serverProcess.HasExited) {
                $exitCode = $serverProcess.ExitCode
                $tail = ""
                if (Test-Path -LiteralPath $stderrLog) {
                    $tail = (Get-Content -LiteralPath $stderrLog -Tail 50 -ErrorAction SilentlyContinue) -join "`n"
                }
                Fail "llama-server exited during startup with code $exitCode.`n`n$tail"
            }

            if (Test-TcpPort -TargetHost $BindHost -TargetPort $Port -and (Test-HttpReady -BaseUrl $baseUrl)) {
                $ready = $true
                break
            }
        }

        if (-not $ready) {
            $tail = ""
            if (Test-Path -LiteralPath $stderrLog) {
                $tail = (Get-Content -LiteralPath $stderrLog -Tail 50 -ErrorAction SilentlyContinue) -join "`n"
            }
            Fail "llama-server did not become ready within $StartupTimeoutSeconds seconds.`n`n$tail"
        }

        Write-Host "llama-server is ready." -ForegroundColor Green
        $effectiveModel = Resolve-ServerModel -BaseUrl $baseUrl -RequestedModel $ModelAlias
    }

    Write-Host "Effective model: $effectiveModel" -ForegroundColor Green

    $env:JARVIS_LOCAL_BASE_URL = $baseUrl
    $env:JARVIS_LOCAL_MODEL = $effectiveModel

    Write-Stage "Regression checks"
    if ($SkipTests) {
        Write-Host "Tests skipped by -SkipTests."
    }
    else {
        Write-Host "Running AI provider regression tests..."
        python -m unittest src.ai.tests.test_local_provider src.ai.tests.test_local_provider_working_context
        if ($LASTEXITCODE -ne 0) {
            Fail "AI provider regression tests failed. JARVIS will not be launched."
        }

        Write-Host "Running core suite..."
        python -m unittest discover -s src\core -p "test*.py"
        if ($LASTEXITCODE -ne 0) {
            Fail "Core tests failed. JARVIS will not be launched."
        }

        Write-Host "Regression checks passed." -ForegroundColor Green
    }

    Write-Stage "Launching JARVIS"
    Write-Host "Endpoint: $env:JARVIS_LOCAL_BASE_URL"
    Write-Host "Model   : $env:JARVIS_LOCAL_MODEL"
    Write-Host "Command : python -m src.run_local_jarvis" -ForegroundColor Green
    Write-Host ""

    python -m src.run_local_jarvis
    $jarvisExitCode = $LASTEXITCODE

    if ($jarvisExitCode -ne 0) {
        Write-Host "JARVIS exited with code $jarvisExitCode." -ForegroundColor Yellow
    }
}
finally {
    Remove-Item Env:JARVIS_LOCAL_BASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_LOCAL_MODEL -ErrorAction SilentlyContinue

    if ($startedByScript -and -not $KeepServer) {
        Stop-StartedServer -Process $serverProcess -StartedByScript $startedByScript
        $serverOwnership = "stopped-after-session"
    }
    elseif ($startedByScript -and $KeepServer) {
        $serverOwnership = "left-running-by-request"
        Write-Host "Keeping llama-server running because -KeepServer was specified." -ForegroundColor Green
    }
}

Write-Stage "JARVIS SESSION ENDED"
Write-Host "Server state: $serverOwnership"
Write-Host ""