Write-Output "Baixando instalador offline do Spotify..."

$spotifyUrl = "https://download.spotify.com/SpotifyFullSetup.exe"
$downloadPath = "$env:TEMP\SpotifyFullSetup.exe"
Invoke-WebRequest -Uri $spotifyUrl -OutFile $downloadPath

Write-Output "Extraindo arquivos do Spotify..."
$installPath = "$env:APPDATA\Spotify"
Start-Process -Wait -FilePath $downloadPath -ArgumentList "/extract $installPath"

# Criação do objeto COM
$WScriptObj = New-Object -ComObject ("WScript.Shell")

Write-Output "Criando atalho na área de trabalho..."
$desktopShortcut = "$env:USERPROFILE\Desktop\Spotify.lnk"
$shortcut = $WScriptObj.CreateShortcut($desktopShortcut)
$shortcut.TargetPath = "$installPath\Spotify.exe"
$shortcut.Save()

Write-Output "Criando atalho no menu iniciar..."
$startMenuShortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"
$shortcut = $WScriptObj.CreateShortcut($startMenuShortcut)
$shortcut.TargetPath = "$installPath\Spotify.exe"
$shortcut.Save()

Write-Output "Registrando Spotify no Painel de Controle..."
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

Write-Output "Fixando Spotify na barra de tarefas..."
# Caminho para o atalho no menu iniciar (necessário para fixar)
$shell = New-Object -ComObject Shell.Application
$folder = $shell.Namespace((Split-Path $startMenuShortcut))
$item = $folder.ParseName((Split-Path $startMenuShortcut -Leaf))

# Executa o verbo "Fixar na barra de tarefas" se estiver disponível
$verbs = $item.Verbs()
foreach ($verb in $verbs) {
    if ($verb.Name.Replace('&','') -match "Fixar.*barra de tarefas") {
        $verb.DoIt()
        break
    }
}

Write-Output "Spotify instalado com sucesso!"
