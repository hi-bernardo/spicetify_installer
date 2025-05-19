Write-Output "Fechando Spotify, se estiver em execução..."
Get-Process -Name Spotify -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Output "Removendo arquivos da instalação..."
$installPath = "$env:APPDATA\Spotify"
Remove-Item -Recurse -Force -Path $installPath -ErrorAction SilentlyContinue

Write-Output "Removendo atalhos..."
$desktopShortcut = "$env:USERPROFILE\Desktop\Spotify.lnk"
$startMenuShortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"
Remove-Item -Force -Path $desktopShortcut -ErrorAction SilentlyContinue
Remove-Item -Force -Path $startMenuShortcut -ErrorAction SilentlyContinue

Write-Output "Removendo entrada do Painel de Controle..."
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Spotify"
Remove-Item -Recurse -Force -Path $regPath -ErrorAction SilentlyContinue

Write-Output "Desinstalação concluída com sucesso!"
