$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $repo 'tmp/desktop-proof/local-rehearsal'
$pg = Join-Path $env:ProgramFiles 'PostgreSQL/18/bin/pg_ctl.exe'
$python = Join-Path $repo 'backend/.venv/Scripts/python.exe'
$health = 'https://localhost:8443/api/health/db'

function Test-RollcallHealth {
    try {
        $body = & curl.exe --fail --silent --max-time 2 $health
        if ($LASTEXITCODE -ne 0) { return $false }
        $response = $body | ConvertFrom-Json
        return $response.status -eq 'ok' -and $response.database -eq 'postgresql'
    } catch {
        return $false
    }
}

if (Test-RollcallHealth) {
    Write-Host 'Rollcall server is already ready.'
    return
}

$data = Join-Path $runtime 'postgres'
$secretFile = Join-Path $runtime 'database-password.dpapi'
$certificate = Join-Path $runtime 'cert.pem'
$key = Join-Path $runtime 'key.pem'
$archive = Join-Path $runtime 'archive'
foreach ($path in @($pg, $python, $data, $secretFile, $certificate, $key, $archive)) {
    if (!(Test-Path -LiteralPath $path)) { throw "Missing Rollcall rehearsal dependency: $path" }
}

& $pg -D $data status | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $pg -D $data -l (Join-Path $runtime 'postgres.log') -o '-h 127.0.0.1 -p 55439' -w -t 20 start
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL could not start. See the local rehearsal postgres.log.' }
}

$password = (Get-Content -LiteralPath $secretFile -Raw).Trim() | ConvertTo-SecureString
$encoded = [uri]::EscapeDataString([Net.NetworkCredential]::new('', $password).Password)
$priorUrl = $env:ROLLCALL_PROOF_DATABASE_URL
$env:ROLLCALL_PROOF_DATABASE_URL = 'postgresql://rollcall_rehearsal:' + $encoded + '@127.0.0.1:55439/rollcall_rehearsal'
try {
    $launch = @{
        FilePath = $python
        WorkingDirectory = $repo
        WindowStyle = 'Hidden'
        PassThru = $true
        ArgumentList = @('backend/serve_desktop_proof.py', '--certificate', ('"' + $certificate + '"'),
            '--key', ('"' + $key + '"'), '--archive', ('"' + $archive + '"'))
        RedirectStandardOutput = Join-Path $runtime 'https-launch.stdout.log'
        RedirectStandardError = Join-Path $runtime 'https-launch.stderr.log'
    }
    $server = Start-Process @launch
    Set-Content -LiteralPath (Join-Path $runtime 'https.pid') -Value $server.Id
} finally {
    $env:ROLLCALL_PROOF_DATABASE_URL = $priorUrl
}

for ($attempt = 0; $attempt -lt 20; $attempt++) {
    if (Test-RollcallHealth) {
        Write-Host 'Rollcall server is ready. Open Rollcall or click Retry.'
        return
    }
    if ($server.HasExited) { break }
    Start-Sleep -Milliseconds 500
}
throw 'Rollcall did not pass its HTTPS health check. See the local rehearsal https-launch.stderr.log and check the localhost certificate.'
