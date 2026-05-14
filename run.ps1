#!/usr/bin/env powershell

<#
.SYNOPSIS
    Knowledge Graph Workflow Runner

.DESCRIPTION
    Script để chạy các workflows: watcher, build, sync

.PARAMETER Command
    watcher - Run file monitor (auto-rebuild)
    build   - Build graph manually
    sync    - Sync from sources and build
    help    - Show help info

.EXAMPLE
    .\run.ps1 watcher
    .\run.ps1 build
    .\run.ps1 sync
#>

param(
    [Parameter(Position=0)]
    [ValidateSet('watcher', 'build', 'sync', 'help', '')]
    [string]$Command = ''
)

# Lấy thư mục script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Activate virtual environment
$venvPath = Join-Path $ScriptDir '.venv'
$activateScript = Join-Path $venvPath 'Scripts\Activate.ps1'

if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Warning "Virtual environment not found at $venvPath"
}

# Process commands
switch ($Command) {
    'watcher' {
        Write-Host ""
        Write-Host "[*] Starting file watcher..." -ForegroundColor Cyan
        Write-Host "[*] Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python watcher.py
    }
    
    'build' {
        Write-Host ""
        Write-Host "[*] Building knowledge graph..." -ForegroundColor Cyan
        Write-Host ""
        python build_graph.py
    }
    
    'sync' {
        Write-Host ""
        Write-Host "[*] Syncing sources and building graph..." -ForegroundColor Cyan
        Write-Host ""
        python sync_and_build.py
    }
    
    'help' {
        Write-Host ""
        Write-Host "Knowledge Graph Workflow - Help" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Green
        Write-Host "  watcher   - Monitor SOURCE_DOCX_PATH and OBSIDIAN_PATH"
        Write-Host "              Automatically builds graph when files change"
        Write-Host ""
        Write-Host "  build     - Build graph from existing KB files"
        Write-Host "              Use to rebuild manually"
        Write-Host ""
        Write-Host "  sync      - Sync from both sources and build graph"
        Write-Host "              Useful for initial setup or full rebuild"
        Write-Host ""
        Write-Host "Configuration:" -ForegroundColor Green
        Write-Host "  Edit .env file to configure paths and settings"
        Write-Host ""
        Write-Host "Documentation:" -ForegroundColor Green
        Write-Host "  Read WORKFLOW.md for detailed information"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Green
        Write-Host "  .\run.ps1 watcher"
        Write-Host "  .\run.ps1 build"
        Write-Host "  .\run.ps1 sync"
        Write-Host ""
    }
    
    '' {
        Write-Host ""
        Write-Host "Usage: .\run.ps1 [command]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Green
        Write-Host "  watcher   - Run file monitor (auto-rebuild)"
        Write-Host "  build     - Build graph manually"
        Write-Host "  sync      - Sync from sources and build"
        Write-Host "  help      - Show help info"
        Write-Host ""
        Write-Host "Run '.\run.ps1 help' for more information" -ForegroundColor Yellow
        Write-Host ""
    }
    
    default {
        Write-Host "[!] Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\run.ps1 help' for usage information" -ForegroundColor Yellow
    }
}
