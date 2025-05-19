$spotifyUrl = "https://download.spotify.com/SpotifyFullSetup.exe"
$downloadPath = "$env:TEMP\SpotifyFullSetup.exe"
Invoke-WebRequest -Uri $spotifyUrl -OutFile $downloadPath

$installPath = "$env:APPDATA\Spotify"
Start-Process -Wait -FilePath $downloadPath -ArgumentList "/extract $installPath"

$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Spotify"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name 'DisplayName' -Value 'Spotify'
Set-ItemProperty -Path $regPath -Name 'DisplayIcon' -Value "$installPath\Spotify.exe,0"
Set-ItemProperty -Path $regPath -Name 'DisplayVersion' -Value ''
Set-ItemProperty -Path $regPath -Name 'Publisher' -Value 'Spotify AB'
Set-ItemProperty -Path $regPath -Name 'UninstallString' -Value "`"$installPath\Spotify.exe`" /uninstall"
Set-ItemProperty -Path $regPath -Name 'InstallLocation' -Value "$installPath"
Set-ItemProperty -Path $regPath -Name 'URLInfoAbout' -Value 'https://www.spotify.com'
Set-ItemProperty -Path $regPath -Name 'NoModify' -Value 1 -Type DWord
Set-ItemProperty -Path $regPath -Name 'NoRepair' -Value 1 -Type DWord
