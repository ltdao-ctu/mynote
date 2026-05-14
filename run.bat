@echo off
REM Batch file để chạy các scripts
REM Các options: watcher, build, sync

setlocal enabledelayedexpansion
cd /d "%~dp0"

if "%1"=="" (
    echo.
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   watcher   - Run file monitor (auto-rebuild graph^)
    echo   build     - Build graph manually
    echo   sync      - Sync from sources and build graph
    echo   help      - Show this help
    echo.
    echo Examples:
    echo   run.bat watcher
    echo   run.bat build
    echo   run.bat sync
    echo.
    goto end
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

if "%1"=="watcher" (
    echo.
    echo [*] Starting file watcher...
    echo [*] Press Ctrl+C to stop
    echo.
    python watcher.py
) else if "%1"=="build" (
    echo.
    echo [*] Building knowledge graph...
    echo.
    python build_graph.py
) else if "%1"=="sync" (
    echo.
    echo [*] Syncing sources and building graph...
    echo.
    python sync_and_build.py
) else if "%1"=="help" (
    echo.
    echo [*] Help information:
    echo.
    echo watcher.py   - Monitors SOURCE_DOCX_PATH and OBSIDIAN_PATH
    echo                Automatically builds graph when files change
    echo.
    echo build_graph.py - Builds graph from existing KB files
    echo                  Use this to rebuild manually
    echo.
    echo sync_and_build.py - Syncs from both sources and builds
    echo                     Useful for initial setup or full rebuild
    echo.
    echo Configuration: Edit .env file
    echo Documentation: Read WORKFLOW.md
    echo.
) else (
    echo [!] Unknown command: %1
    echo Run "run.bat help" for usage
)

:end
endlocal
