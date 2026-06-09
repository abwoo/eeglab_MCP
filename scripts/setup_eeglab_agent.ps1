param(
    [switch]$DryRun,
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$EeglabPath = "D:\MATLAB_Tools\eeglab",
    [string]$MatlabRoot = "D:\MATLAB",
    [string]$MatlabExec = "matlab",
    [string]$EeglabWorkDir = "$env:USERPROFILE\Desktop\eeglabmcp",
    [string]$MatlabTimeout = "300"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ServerPath = Join-Path $RepoRoot "eeglab_mcp_server\server.py"
$SkillSource = Join-Path $RepoRoot "skills\eeglab-analysis"
$ConfigPath = Join-Path $CodexHome "config.toml"
$SkillTarget = Join-Path $CodexHome "skills\eeglab-analysis"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

function New-EeglabConfigBlock {
    @"
[mcp_servers.eeglab]
command = "python"
args = ['$ServerPath']
startup_timeout_sec = 120

[mcp_servers.eeglab.env]
EEGLAB_PATH = '$EeglabPath'
MATLAB_ROOT = '$MatlabRoot'
MATLAB_EXEC = "$MatlabExec"
EEGLAB_WORK_DIR = '$EeglabWorkDir'
MATLAB_TIMEOUT = "$MatlabTimeout"
"@
}

function Remove-EeglabConfigBlock {
    param([string]$Text)
    $lines = $Text -split "`r?`n"
    $out = New-Object System.Collections.Generic.List[string]
    $skip = $false
    foreach ($line in $lines) {
        if ($line -match '^\[mcp_servers\.eeglab\]$' -or $line -match '^\[mcp_servers\.eeglab\.env\]$') {
            $skip = $true
            continue
        }
        if ($skip -and $line -match '^\[') {
            $skip = $false
        }
        if (-not $skip) {
            $out.Add($line)
        }
    }
    return (($out -join "`r`n").TrimEnd() + "`r`n")
}

if (-not (Test-Path -LiteralPath $ServerPath)) {
    throw "Missing server: $ServerPath"
}
if (-not (Test-Path -LiteralPath $SkillSource)) {
    throw "Missing skill: $SkillSource"
}

$existingText = ""
if (Test-Path -LiteralPath $ConfigPath) {
    $existingText = Get-Content -Raw -LiteralPath $ConfigPath
}
$hasMatlabMcp = $existingText -match '(?m)^\[mcp_servers\.matlab\]$'
$newText = (Remove-EeglabConfigBlock -Text $existingText).TrimEnd()
if ($newText.Length -gt 0) {
    $newText += "`r`n`r`n"
}
$newText += (New-EeglabConfigBlock) + "`r`n"

Write-Host "EEGLAB agent setup"
Write-Host "repo_root=$RepoRoot"
Write-Host "codex_config=$ConfigPath"
Write-Host "skill_target=$SkillTarget"
Write-Host "matlab_mcp_present=$hasMatlabMcp"
Write-Host "dry_run=$DryRun"

if ($DryRun) {
    Write-Host ""
    Write-Host "Would write MCP block:"
    Write-Host (New-EeglabConfigBlock)
    Write-Host ""
    Write-Host "Would sync skill from $SkillSource to $SkillTarget"
    exit 0
}

New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
if (Test-Path -LiteralPath $ConfigPath) {
    Copy-Item -LiteralPath $ConfigPath -Destination "$ConfigPath.bak-$Timestamp" -Force
}
Set-Content -LiteralPath $ConfigPath -Value $newText -Encoding UTF8

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SkillTarget) | Out-Null
if (Test-Path -LiteralPath $SkillTarget) {
    Copy-Item -LiteralPath $SkillTarget -Destination "$SkillTarget.bak-$Timestamp" -Recurse -Force
    Remove-Item -LiteralPath $SkillTarget -Recurse -Force
}
Copy-Item -LiteralPath $SkillSource -Destination $SkillTarget -Recurse -Force

Write-Host "setup_status=success"
Write-Host "next_step=Restart Codex, then run scripts\doctor_eeglab_agent.ps1"
