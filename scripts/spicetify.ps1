$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

#region Variables
$spicetifyFolderPath = "$env:LOCALAPPDATA\spicetify"
$spicetifyOldFolderPath = "$HOME\spicetify-cli"
#endregion Variables

#region Functions
function Write-Success {
  param ()
  Write-Host ' > OK' -ForegroundColor 'Green'
}

function Write-Unsuccess {
  param ()
  Write-Host ' > ERROR' -ForegroundColor 'Red'
}

function Test-Admin {
  param ()
  Write-Host "Checking if the script is not being run as administrator..." -NoNewline
  $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Success
  } else {
    Write-Unsuccess
    Write-Warning "The script is running as administrator. This can cause issues but will continue."
  }
}

function Install-Spicetify {
  param ()
  Write-Host 'Installing spicetify...'
  $archivePath = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "spicetify.zip")
  Invoke-WebRequest -Uri "https://github.com/spicetify/cli/releases/latest/download/spicetify-windows.zip" -OutFile $archivePath
  Expand-Archive -Path $archivePath -DestinationPath $spicetifyFolderPath -Force
  Write-Success
  Remove-Item -Path $archivePath -Force -ErrorAction 'SilentlyContinue'
  Write-Host 'spicetify was successfully installed!' -ForegroundColor 'Green'
}

function Install-Marketplace {
  param ()
  Write-Host 'Installing Spicetify Marketplace...'
  Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/spicetify/spicetify-marketplace/main/resources/install.ps1' -UseBasicParsing | Invoke-Expression
  Write-Success
}
#endregion Functions

#region Main
Test-Admin
Install-Spicetify
Install-Marketplace
Write-Host "\nRun" -NoNewline
Write-Host ' spicetify -h ' -NoNewline -ForegroundColor 'Cyan'
Write-Host 'to get started'
#endregion Main
#region Custom Apps Installation
Write-Host -Object 'Installing lyrics-plus app...' -NoNewline
spicetify config custom_apps lyrics-plus enable-devtools
spicetify apply
Write-Success
#endregion Custom Apps Installation
#endregion Main
