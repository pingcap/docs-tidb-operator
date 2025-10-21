<#
.SYNOPSIS
Runs Markdown validation for the docs repository.

.DESCRIPTION
This is a convenience wrapper for Windows users to run the Python-based
validator without remembering arguments.

.PARAMETER Paths
Optional list of files or directories to validate. Defaults to 'en' and 'zh'.

.EXAMPLE
  ./scripts/validate-docs.ps1
  ./scripts/validate-docs.ps1 en README.md
#>

param(
    [Parameter(Mandatory=$false, Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Paths
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

if (-not $Paths -or $Paths.Count -eq 0) {
    $Paths = @('en', 'zh')
}

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Error "Python not found in PATH. Please install Python 3.8+"
    exit 2
}

& $py.Path "$ScriptDir/validate_docs.py" --repo-root "$RepoRoot" --format text @Paths
$exitCode = $LASTEXITCODE
exit $exitCode


