# Instala o Spotify (versão EXE)
winget install --id=Spotify.Spotify -e --accept-package-agreements --accept-source-agreements

# Aguarda 3 segundos após o término da instalação
Start-Sleep -Seconds 3

# Caminho do executável
$spotifyPath = "$env:APPDATA\Spotify\Spotify.exe"

# Verifica se o executável existe e executa
if (Test-Path $spotifyPath) {
    Start-Process $spotifyPath
} else {
    Write-Host "Spotify.exe não encontrado em $spotifyPath"
}
