@echo off
REM EEGLAB MCP Server launcher
REM Usage: start_eeglab_mcp.bat [EEGLAB path]

setlocal

REM Set the EEGLAB path (given as an argument or through an environment variable)
if "%~1" neq "" (
    set EEGLAB_PATH=%~1
)

REM Set the project directory
set SERVER_DIR=%~dp0

REM Launch the MCP server
cd /d "%SERVER_DIR%"
python server.py

endlocal
