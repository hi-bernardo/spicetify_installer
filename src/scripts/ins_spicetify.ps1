$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

#region Variables
$spicetifyFolderPath = "$env:LOCALAPPDATA\spicetify"
$spicetifyOldFolderPath = "$HOME\spicetify-cli"
#endregion

#region Functions
function Write-Success {
  Write-Host ' > OK' -ForegroundColor Green
}
function Write-Unsuccess {
  Write-Host ' > ERROR' -ForegroundColor Red
}
function Test-PowerShellVersion {
  $PSMinVersion = [version]'5.1'
  Write-Host 'Checking PowerShell version...' -NoNewline
  if ($PSVersionTable.PSVersion -ge $PSMinVersion) { Write-Success; return $true }
  else { Write-Unsuccess; exit 1 }
}
function Move-OldSpicetifyFolder {
  if (Test-Path $spicetifyOldFolderPath) {
    Write-Host 'Moving old spicetify folder...' -NoNewline
    Copy-Item "$spicetifyOldFolderPath\*" -Destination $spicetifyFolderPath -Recurse -Force
    Remove-Item $spicetifyOldFolderPath -Recurse -Force
    Write-Success
  }
}
function Get-Spicetify {
  Write-Host 'Fetching latest spicetify version...' -NoNewline
  $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'AMD64') {'x64'} elseif ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {'arm64'} else {'x32'}
  $latest = (Invoke-RestMethod 'https://api.github.com/repos/spicetify/cli/releases/latest').tag_name -replace 'v',''
  Write-Success
  $url = "https://github.com/spicetify/cli/releases/download/v$latest/spicetify-$latest-windows-$arch.zip"
  $zipPath = "$env:TEMP\spicetify.zip"
  Write-Host "Downloading spicetify v$latest..." -NoNewline
  Invoke-WebRequest $url -OutFile $zipPath -UseBasicParsing
  Write-Success
  return $zipPath
}
function Add-SpicetifyToPath {
  Write-Host 'Adding spicetify to PATH...' -NoNewline
  $user = [EnvironmentVariableTarget]::User
  $path = [Environment]::GetEnvironmentVariable('PATH', $user)
  if ($path -notlike "*$spicetifyFolderPath*") {
    $path += ";$spicetifyFolderPath"
    [Environment]::SetEnvironmentVariable('PATH', $path, $user)
    $env:PATH = $path
  }
  Write-Success
}
function Install-Spicetify {
  Write-Host 'Installing spicetify...'
  $zip = Get-Spicetify
  Write-Host 'Extracting spicetify...' -NoNewline
  Expand-Archive -Path $zip -DestinationPath $spicetifyFolderPath -Force
  Write-Success
  Remove-Item $zip -Force
  Add-SpicetifyToPath
  Write-Host 'Spicetify installed!' -ForegroundColor Green
}
function Install-Marketplace {
  Write-Host 'Installing Spicetify Marketplace...' -NoNewline
  Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/spicetify/spicetify-marketplace/main/resources/install.ps1' -UseBasicParsing | Invoke-Expression
  Write-Success
}
#endregion

#region Main
Test-PowerShellVersion
Move-OldSpicetifyFolder
Install-Spicetify
Install-Marketplace

Write-Host 'Installing lyrics-plus app...' -NoNewline
spicetify config custom_apps lyrics-plus enable-devtools
spicetify apply
Write-Success
#endregion
