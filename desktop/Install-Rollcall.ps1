# Run from the extracted rehearsal package as the workstation user.
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'client'
$manifest = Get-Content -LiteralPath (Join-Path $source 'resources/app/package.json') -Raw | ConvertFrom-Json
if ($manifest.name -ne 'rollcall-desktop' -or $manifest.version -notmatch '^\d+\.\d+\.\d+$') {
    throw 'The Rollcall package metadata is invalid.'
}
if (!(Test-Path -LiteralPath (Join-Path $source 'Rollcall.exe') -PathType Leaf)) {
    throw 'Extract the complete Rollcall ZIP before installing.'
}

$root = Join-Path $env:LOCALAPPDATA 'Rollcall'
$destination = Join-Path $root $manifest.version
$programs = Join-Path $env:APPDATA 'Microsoft/Windows/Start Menu/Programs'
New-Item -ItemType Directory -Path $root, $programs -Force | Out-Null
if (!(Test-Path -LiteralPath $destination)) {
    $staging = Join-Path $root ('.install-' + [guid]::NewGuid().ToString())
    Copy-Item -LiteralPath $source -Destination $staging -Recurse
    [System.IO.Directory]::Move($staging, $destination)
}

$exe = Join-Path $destination 'Rollcall.exe'
if (!(Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw 'An incomplete version already exists in the installation directory.'
}
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $programs 'Rollcall.lnk'))
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $destination
$shortcut.Description = 'Rollcall desktop client'
$shortcut.Save()
Write-Output "Rollcall $($manifest.version) installed. Open Rollcall from Start."
