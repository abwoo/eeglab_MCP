param(
    [ValidateSet("help", "setup", "verify", "verify-online", "doctor", "uninstall")]
    [string]$Action = "help",
    [switch]$DryRun,
    [switch]$Online,
    [switch]$SkipCompile,
    [switch]$RemoveSkill,
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$EeglabPath = "D:\MATLAB_Tools\eeglab",
    [string]$MatlabRoot = "D:\MATLAB",
    [string]$MatlabExec = "matlab",
    [string]$EeglabWorkDir = "$env:USERPROFILE\Desktop\eeglabmcp",
    [string]$MatlabTimeout = "300"
)

$ErrorActionPreference = "Stop"

$SetupScript = Join-Path $PSScriptRoot "setup_eeglab_agent.ps1"
$VerifyScript = Join-Path $PSScriptRoot "verify_eeglab_agent.ps1"
$DoctorScript = Join-Path $PSScriptRoot "doctor_eeglab_agent.ps1"
$UninstallScript = Join-Path $PSScriptRoot "uninstall_eeglab_agent.ps1"

function Show-EeglabAgentHelp {
    Write-Host "EEGLAB MCP Agent command dispatcher"
    Write-Host ""
    Write-Host "Common commands:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -DryRun -RemoveSkill"
    Write-Host ""
    Write-Host "This dispatcher only routes to the dedicated scripts; scientific gates remain enforced by the MCP tools and verifiers."
}

switch ($Action) {
    "help" {
        Show-EeglabAgentHelp
    }
    "setup" {
        $setupArgs = @(
            "-CodexHome", $CodexHome,
            "-EeglabPath", $EeglabPath,
            "-MatlabRoot", $MatlabRoot,
            "-MatlabExec", $MatlabExec,
            "-EeglabWorkDir", $EeglabWorkDir,
            "-MatlabTimeout", $MatlabTimeout
        )
        if ($DryRun) {
            $setupArgs += "-DryRun"
        }
        & $SetupScript @setupArgs
    }
    "verify" {
        if ($Online -and $SkipCompile) {
            & $VerifyScript -Online -SkipCompile
        } elseif ($Online) {
            & $VerifyScript -Online
        } elseif ($SkipCompile) {
            & $VerifyScript -SkipCompile
        } else {
            & $VerifyScript
        }
    }
    "verify-online" {
        if ($SkipCompile) {
            & $VerifyScript -Online -SkipCompile
        } else {
            & $VerifyScript -Online
        }
    }
    "doctor" {
        & $DoctorScript -CodexHome $CodexHome -EeglabPath $EeglabPath -MatlabExec $MatlabExec
    }
    "uninstall" {
        $uninstallArgs = @("-CodexHome", $CodexHome)
        if ($DryRun) {
            $uninstallArgs += "-DryRun"
        }
        if ($RemoveSkill) {
            $uninstallArgs += "-RemoveSkill"
        }
        & $UninstallScript @uninstallArgs
    }
}
