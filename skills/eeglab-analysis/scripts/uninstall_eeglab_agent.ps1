param(
    [switch]$DryRun,
    [switch]$RemoveSkill,
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"

$ConfigPath = Join-Path $CodexHome "config.toml"
$SkillTarget = Join-Path $CodexHome "skills\eeglab-analysis"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

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

Write-Host "EEGLAB agent uninstall"
Write-Host "codex_config=$ConfigPath"
Write-Host "remove_skill=$RemoveSkill"
Write-Host "dry_run=$DryRun"

if (Test-Path -LiteralPath $ConfigPath) {
    $existingText = Get-Content -Raw -LiteralPath $ConfigPath
    $newText = Remove-EeglabConfigBlock -Text $existingText
    if ($DryRun) {
        Write-Host "Would remove [mcp_servers.eeglab] blocks from $ConfigPath"
    } else {
        Copy-Item -LiteralPath $ConfigPath -Destination "$ConfigPath.bak-uninstall-$Timestamp" -Force
        Set-Content -LiteralPath $ConfigPath -Value $newText -Encoding UTF8
        Write-Host "removed_eeglab_mcp_config=True"
    }
}

if ($RemoveSkill -and (Test-Path -LiteralPath $SkillTarget)) {
    if ($DryRun) {
        Write-Host "Would remove skill directory $SkillTarget"
    } else {
        Copy-Item -LiteralPath $SkillTarget -Destination "$SkillTarget.bak-uninstall-$Timestamp" -Recurse -Force
        Remove-Item -LiteralPath $SkillTarget -Recurse -Force
        Write-Host "removed_skill=True"
    }
}

Write-Host "uninstall_status=success"
