# ----------------------------------------------------------------------------
<#
.SYNOPSIS
Launches a selected free Ollama Cloud model for Claude Code.

.DESCRIPTION
Fetches the latest list of free models from the remote catalog, ranks them based on a coding‑first priority, prompts the user to select a model (or accepts the top recommendation), maps the selection to the appropriate Ollama Cloud identifier, and launches the model. Includes fallback handling for new catalog entries and ensures Ollama is installed.

.PARAMETER None
No parameters; interaction occurs via prompts.

.EXAMPLE
./launch_free_model_fixed_v3.ps1
Prompts and launches the recommended free model.
#>
# ----------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$MyFolder = 'D:\AI\StockPrediction2026'
Set-Location $MyFolder
$workingDirectory = $MyFolder

# ----------------------------------------------------------------------------
$url = 'https://raw.githubusercontent.com/syedkhalid0/OllamaCloud-Free-Models/main/models.json'

Clear-Host
Write-Host 'Fetching latest free cloud models...' -ForegroundColor Cyan

if (Test-Path -LiteralPath $workingDirectory -PathType Container) {
    Set-Location -LiteralPath $workingDirectory
}
else {
    Write-Warning "Working directory not found: $workingDirectory"
}

if (-not (Get-Command 'ollama' -ErrorAction SilentlyContinue)) {
    Write-Host 'Error: Ollama was not found on PATH. Install/update Ollama or correct PATH, then retry.' -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------------
try {
    $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 20 -ErrorAction Stop

    if ($null -eq $response) {
        throw 'The model catalog returned an empty response.'
    }

    $freeModels = @(
        $response |
            Where-Object {
                $_.isFree -eq $true -and
                -not [string]::IsNullOrWhiteSpace([string]$_.model)
            } |
            ForEach-Object { ([string]$_.model).Trim() } |
            Sort-Object -Unique
    )
}
catch {
    Write-Host "Error: Could not download or parse the model list. $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------------
if ($freeModels.Count -eq 0) {
    Write-Host 'No free models were found in the catalog.' -ForegroundColor Yellow
    exit 1
}

# ----------------------------------------------------------------------------
# Curated coding-first preference order. This is a practical heuristic, not a live benchmark.
# Only models currently marked free by the repository can appear in the menu.
$codingPriority = @(
    'beam',
    'gpt-oss:120b',
    'nemotron-3-super',
    'gemma4:31b',
    'nemotron-3-ultra',
    'nemotron-3-nano:30b',
    'gpt-oss:20b'
)

# ----------------------------------------------------------------------------
# Use an explicit map for known Ollama Cloud identifiers. Naming conventions differ by model.
$cloudIdMap = @{
    'beam'                    = 'beam:cloud'
    'gpt-oss:120b'            = 'gpt-oss:120b-cloud'
    'gpt-oss:20b'             = 'gpt-oss:20b-cloud'
    'nemotron-3-super'        = 'nemotron-3-super:cloud'
    'nemotron-3-ultra'        = 'nemotron-3-ultra:cloud'
    'nemotron-3-nano:30b'     = 'nemotron-3-nano:30b-cloud'
    'gemma4:31b'              = 'gemma4:31b-cloud'
}

# ----------------------------------------------------------------------------
# Rank known models by the curated coding preference; place newly listed models at the end.
$rankedModels = @(
    $freeModels | Sort-Object -Unique | Sort-Object {
        $position = [array]::IndexOf($codingPriority, $_)
        if ($position -lt 0) { 999 } else { $position }
    }, { $_ }
)

# ----------------------------------------------------------------------------
$recommendedModel = $rankedModels[0]
Write-Host "`nFree Ollama Cloud Models for Python Coding" -ForegroundColor Green
Write-Host "Recommended first choice: $recommendedModel" -ForegroundColor Cyan
Write-Host 'Ranking is a curated coding-oriented heuristic, not a live benchmark; availability comes from the repository.' -ForegroundColor DarkGray
Write-Host ''

for ($i = 0; $i -lt $rankedModels.Count; $i++) {
    $model = $rankedModels[$i]
    $note = ''
    if ($i -eq 0) { $note = '  <-- Recommended for Python coding' }
    elseif ($model -eq 'gpt-oss:120b') { $note = '  (strong general reasoning alternative)' }
    elseif ($model -eq 'nemotron-3-super') { $note = '  (agentic/reasoning alternative)' }
    Write-Host (' [{0}] {1}{2}' -f ($i + 1), $model, $note)
}

Write-Host ''
$choice = Read-Host 'Select a model number, or press Enter for the recommendation'

if ([string]::IsNullOrWhiteSpace($choice)) {
    $selectedModel = $recommendedModel
}
else {
    [int]$index = 0
    if (-not [int]::TryParse($choice, [ref]$index) -or $index -lt 1 -or $index -gt $rankedModels.Count) {
        Write-Host 'Invalid selection. Exiting.' -ForegroundColor Red
        exit 1
    }
    $selectedModel = $rankedModels[$index - 1]
}

if ($cloudIdMap.ContainsKey($selectedModel)) {
    $modelToLaunch = $cloudIdMap[$selectedModel]
}
elseif ($selectedModel -match ':(cloud)$' -or $selectedModel -match '-cloud$') {
    $modelToLaunch = $selectedModel
}
elseif ($selectedModel -notmatch ':') {
    # Fallback for new untagged catalog entries. Verify the resulting ID if Ollama rejects it.
    $modelToLaunch = "${selectedModel}:cloud"
}
else {
    # Fallback for new tagged catalog entries, following Ollama's tagged cloud naming convention.
    $modelToLaunch = "${selectedModel}-cloud"
}

# ----------------------------------------------------------------------------
Write-Host "`nLaunching Claude Code with Ollama Cloud model: $modelToLaunch" -ForegroundColor Cyan
Write-Host 'Cloud models should not require downloading model weights. If Ollama offers a large local model download, cancel and verify that Ollama is up to date and the model ID is correct.' -ForegroundColor Yellow

try {
    & ollama launch claude --model $modelToLaunch
    $ollamaExitCode = $LASTEXITCODE

    if ($ollamaExitCode -ne 0) {
        Write-Host "Ollama exited with code $ollamaExitCode." -ForegroundColor Red
        exit $ollamaExitCode
    }
}
catch {
    Write-Host "Error: Failed to launch Ollama. $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
