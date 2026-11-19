$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    foreach ($command in @('npm', 'uv')) {
        if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
            throw "Install $command before running setup. See README.md."
        }
    }
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
    }
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    uv sync --all-packages --locked
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    Write-Host 'Dependencies ready. See README.md for startup commands.'
}
finally {
    Pop-Location
}
