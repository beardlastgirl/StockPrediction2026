$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { throw "venv not found: $venvPy" }
$env:PYTHONWARNINGS = "ignore"
& $venvPy -m eventstudy @args
