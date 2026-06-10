param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$EeglabPath = "D:\MATLAB_Tools\eeglab",
    [string]$MatlabExec = "matlab"
)

$ErrorActionPreference = "Continue"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ConfigPath = Join-Path $CodexHome "config.toml"
$SkillTarget = Join-Path $CodexHome "skills\eeglab-analysis\SKILL.md"
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
Add-Check "codex_config_exists" (Test-Path -LiteralPath $ConfigPath) "Run scripts\setup_eeglab_agent.ps1."
Add-Check "eeglab_mcp_registered" ($configText -match '(?m)^\[mcp_servers\.eeglab\]$') "Run scripts\setup_eeglab_agent.ps1."
Add-Check "matlab_mcp_registered" ($configText -match '(?m)^\[mcp_servers\.matlab\]$') "Optional: register a general matlab MCP if you need custom MATLAB scripts."
Add-Check "skill_installed" (Test-Path -LiteralPath $SkillTarget) "Run scripts\setup_eeglab_agent.ps1 to sync the skill."

try {
    $mcpCheck = @'
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["-B", "eeglab_mcp_server/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            prompts = await session.list_prompts()
            resources = await session.list_resources()
            tool_names = {tool.name for tool in tools.tools}
            legacy = {
                "eeglab_init", "eeglab_load_data", "eeglab_save_data", "eeglab_import_bids",
                "eeglab_info", "eeglab_history", "eeglab_filter", "eeglab_resample",
                "eeglab_reref", "eeglab_select_channels", "eeglab_interpolate_channels",
                "eeglab_edit_channels", "eeglab_clean_line_noise", "eeglab_clean_rawdata",
                "eeglab_run_ica", "eeglab_classify_ica", "eeglab_flag_components",
                "eeglab_remove_components", "eeglab_reject_epochs", "eeglab_get_events",
                "eeglab_epoch", "eeglab_erp_analysis", "eeglab_sort_epochs",
                "eeglab_average_erp", "eeglab_spectral", "eeglab_timefreq",
                "eeglab_connectivity", "eeglab_topoplot", "eeglab_plot_erp",
                "eeglab_plot_timefreq", "eeglab_plot_components", "eeglab_source_localization",
                "eeglab_source_settings", "eeglab_study_create", "eeglab_study_design",
                "eeglab_study_statistics", "eeglab_pipeline", "eeglab_qc_report",
                "eeglab_erp_light_workflow", "eeglab_workflow_recommend"
            }
            research = {"eeglab_project_plan", "eeglab_protocol_export", "eeglab_plugin_check", "eeglab_event_semantics_audit"}
            prompt_names = {prompt.name for prompt in prompts.prompts}
            resource_uris = {str(resource.uri) for resource in resources.resources}
            print(f"tool_count={len(tools.tools)}")
            print(f"legacy_tools_present={legacy.issubset(tool_names)}")
            print(f"research_tools_present={research.issubset(tool_names)}")
            print(f"prompt_count={len(prompts.prompts)}")
            print(f"resource_count={len(resources.resources)}")
            print(f"official_resource_present={'eeglab://official/references.md' in resource_uris}")

asyncio.run(main())
'@
    $output = $mcpCheck | python -B -
    $ok = ($LASTEXITCODE -eq 0) -and ($output -match 'legacy_tools_present=True') -and ($output -match 'research_tools_present=True') -and ($output -match 'official_resource_present=True')
    Add-Check "mcp_stdio_smoke" $ok "Inspect Python dependencies and run python -B scripts\verify_framework.py."
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
