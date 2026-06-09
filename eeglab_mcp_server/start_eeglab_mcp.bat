@echo off
REM EEGLAB MCP Server 启动脚本
REM 使用方法: start_eeglab_mcp.bat [EEGLAB路径]

setlocal

REM 设置 EEGLAB 路径（可通过参数或环境变量指定）
if "%~1" neq "" (
    set EEGLAB_PATH=%~1
)

REM 设置项目目录
set SERVER_DIR=%~dp0

REM 启动 MCP 服务器
cd /d "%SERVER_DIR%"
python server.py

endlocal
