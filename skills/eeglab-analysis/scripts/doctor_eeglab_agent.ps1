param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$EeglabPath = "D:\MATLAB_Tools\eeglab",
    [string]$MatlabExec = "matlab"
)

$ErrorActionPreference = "Continue"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ConfigPath = Join-Path $CodexHome "config.toml"
$SkillRoot = Join-Path $CodexHome "skills\eeglab-analysis"
$SkillTarget = Join-Path $SkillRoot "SKILL.md"
$SkillReportScript = Join-Path $SkillRoot "scripts\generate_eeg_report.py"
$SkillReportTemplate = Join-Path $SkillRoot "scripts\report_template.json"
$SkillDocsRoot = Join-Path $SkillRoot "docs"
$ServerPath = Join-Path $RepoRoot "eeglab_mcp_server\server.py"

$results = [ordered]@{}

function Add-Check {
    param([string]$Name, [bool]$Ok, [string]$NextStep = "")
    $results[$Name] = [ordered]@{ ok = $Ok; next_step = $NextStep }
    $status = if ($Ok) { "ok" } else { "fail" }
    Write-Host "$Name=$status"
    if (-not $Ok -and $NextStep) {
        Write-Host "$Name.next_step=$NextStep"
    }
}

Add-Check "python_available" ([bool](Get-Command python -ErrorAction SilentlyContinue)) "Install Python 3.10+ and ensure python is on PATH."
Add-Check "server_exists" (Test-Path -LiteralPath $ServerPath) "Run this doctor script from the EEGLAB MCP repository."
Add-Check "eeglab_path_exists" (Test-Path -LiteralPath $EeglabPath) "Set -EeglabPath to the local EEGLAB installation."
Add-Check "matlab_exec_available" ([bool](Get-Command $MatlabExec -ErrorAction SilentlyContinue)) "Set -MatlabExec to matlab.exe or add MATLAB to PATH."

$configText = ""
if (Test-Path -LiteralPath $ConfigPath) {
    $configText = Get-Content -Raw -LiteralPath $ConfigPath
}
Add-Check "codex_config_exists" (Test-Path -LiteralPath $ConfigPath) "Run scripts\eeglab_agent.ps1 setup."
Add-Check "eeglab_mcp_registered" ($configText -match '(?m)^\[mcp_servers\.eeglab\]\r?$') "Run scripts\eeglab_agent.ps1 setup."
Add-Check "matlab_mcp_registered" ($configText -match '(?m)^\[mcp_servers\.matlab\]\r?$') "Optional: register a general matlab MCP if you need custom MATLAB scripts."
Add-Check "skill_installed" (Test-Path -LiteralPath $SkillTarget) "Run scripts\eeglab_agent.ps1 setup to sync the skill."
Add-Check "skill_report_script_installed" (Test-Path -LiteralPath $SkillReportScript) "Run scripts\eeglab_agent.ps1 setup to sync bundled skill scripts."
Add-Check "skill_report_template_installed" (Test-Path -LiteralPath $SkillReportTemplate) "Run scripts\eeglab_agent.ps1 setup to sync bundled report templates."
$skillDocsCount = 0
if (Test-Path -LiteralPath $SkillDocsRoot) {
    $skillDocsCount = @(Get-ChildItem -LiteralPath $SkillDocsRoot -Filter "*.md" -File).Count
}
Add-Check "skill_docs_installed" ($skillDocsCount -ge 10) "Run scripts\eeglab_agent.ps1 setup to sync bundled official docs."
Write-Host "skill_docs_count=$skillDocsCount"

try {
    $mcpCheck = @'
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from eeglab_mcp_server.tool_registry import (
    LEGACY_LOW_LEVEL_TOOL_NAMES,
    RESEARCH_WORKFLOW_TOOL_NAMES,
)

async def main():
    params = StdioServerParameters(command="python", args=["-B", "eeglab_mcp_server/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            prompts = await session.list_prompts()
            resources = await session.list_resources()
            tool_names = {tool.name for tool in tools.tools}
            prompt_names = {prompt.name for prompt in prompts.prompts}
            resource_uris = {str(resource.uri) for resource in resources.resources}
            print(f"tool_count={len(tools.tools)}")
            print(f"legacy_tools_present={LEGACY_LOW_LEVEL_TOOL_NAMES.issubset(tool_names)}")
            print(f"research_tools_present={RESEARCH_WORKFLOW_TOOL_NAMES.issubset(tool_names)}")
            print(f"prompt_count={len(prompts.prompts)}")
            print(f"resource_count={len(resources.resources)}")
            official_resources = {
                "eeglab://official/references.md",
                "eeglab://official/method-map.md",
                "eeglab://official/gate-policy.md",
                "eeglab://official/plugin-map.md",
            }
            print(f"official_resource_present={official_resources.issubset(resource_uris)}")

asyncio.run(main())
'@
    $output = $mcpCheck | python -B -
    $ok = ($LASTEXITCODE -eq 0) -and ($output -match 'legacy_tools_present=True') -and ($output -match 'research_tools_present=True') -and ($output -match 'official_resource_present=True')
    Add-Check "mcp_stdio_smoke" $ok "Inspect Python dependencies and run scripts\eeglab_agent.ps1 verify."
    $output | ForEach-Object { Write-Host $_ }
}
catch {
    Add-Check "mcp_stdio_smoke" $false $_.Exception.Message
}

$failed = @($results.GetEnumerator() | Where-Object { -not $_.Value.ok })
Write-Host "doctor_failed_count=$($failed.Count)"
if ($failed.Count -eq 0) {
    Write-Host "doctor_status=success"
} else {
    Write-Host "doctor_status=needs_attention"
}
