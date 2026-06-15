param(
    [switch]$Online,
    [switch]$SkipCompile
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $RepoRoot

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Command $($Arguments -join ' ')"
    }
}

try {
    Write-Host "verify_repo=$RepoRoot"

    if (-not $SkipCompile) {
        Write-Host "step=source_compile"
        $pythonFiles = @(
            Get-ChildItem -LiteralPath ".\eeglab_mcp_server" -Filter "*.py" -File
            Get-ChildItem -LiteralPath ".\scripts" -Filter "verify_*.py" -File
        ) | ForEach-Object { $_.FullName }
        $compileCheck = @'
import sys

ok = True
for path in sys.argv[1:]:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    try:
        compile(source, path, "exec")
    except SyntaxError as exc:
        ok = False
        print("%s:%s:%s: %s" % (path, exc.lineno, exc.offset, exc.msg))

if not ok:
    raise SystemExit(1)
'@
        $compileCheck | python -B - @pythonFiles
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE`: python -B - <source compile check>"
        }
    }

    Write-Host "step=framework"
    Invoke-Checked python -B .\scripts\verify_framework.py

    Write-Host "step=official_alignment"
    Invoke-Checked python -B .\scripts\verify_official_alignment.py

    if ($Online) {
        Write-Host "step=official_alignment_online"
        Invoke-Checked python -B .\scripts\verify_official_alignment.py --online
    }

    Write-Host "verify_status=success"
}
finally {
    Pop-Location
}
