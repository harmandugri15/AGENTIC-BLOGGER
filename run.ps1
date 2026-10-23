<#
.SYNOPSIS
    Enterprise Multi-Agent Platform PowerShell Runner
.DESCRIPTION
    Replaces batch scripts with native, type-safe PowerShell process management.
.EXAMPLE
    .\run.ps1 start
    .\run.ps1 backend
    .\run.ps1 frontend
    .\run.ps1 test
#>

param (
    [ValidateSet("start", "dev", "backend", "frontend", "test", "build", "status")]
    [string]$Command = "start"
)

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot

function Write-Log {
    param([string]$Tag, [string]$Message, [ConsoleColor]$Color = [ConsoleColor]::Cyan)
    $timestamp = (Get-Date).ToString("HH:mm:ss")
    Write-Host "[$timestamp] [$Tag] " -NoNewline -ForegroundColor $Color
    Write-Host $Message
}

switch ($Command) {
    { $_ -in "start", "dev" } {
        Write-Log "RUNNER" "Starting unified dev services..." -Color Green
        python "$RootDir\run.py" dev
    }
    "backend" {
        Write-Log "BACKEND" "Starting FastAPI Backend on http://127.0.0.1:8000..." -Color Magenta
        $env:PYTHONPATH = $RootDir
        python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    "frontend" {
        Write-Log "FRONTEND" "Starting Vite Frontend Dashboard..." -Color Cyan
        Set-Location "$RootDir\frontend"
        npm run dev
    }
    "test" {
        Write-Log "TEST" "Running backend tests..." -Color Cyan
        Set-Location $RootDir
        python -m pytest backend/tests -v
    }
    "build" {
        Write-Log "BUILD" "Building frontend for production..." -Color Cyan
        Set-Location "$RootDir\frontend"
        npm run build
    }
    "status" {
        python "$RootDir\run.py" status
    }
}
