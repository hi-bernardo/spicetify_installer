$ErrorActionPreference = "Stop"

#region Spotify INSTALLER SCRIPT START

# Fecha o Spotify se estiver em execução
Write-Host "`n[1/4] Verificando se o Spotify está em execução..." -ForegroundColor Cyan
$spotifyProc = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if ($spotifyProc) {
    Write-Host " > Spotify está em execução. Encerrando..." -ForegroundColor Yellow
    Stop-Process -Name Spotify -Force
    Start-Sleep -Seconds 2
    Write-Host " > Processo encerrado com sucesso." -ForegroundColor Green
} else {
    Write-Host " > Spotify não está em execução." -ForegroundColor Green
}

# Instala o Spotify com winget
Write-Host "`n[2/4] Instalando o Spotify via winget..." -ForegroundColor Cyan
winget install --id=Spotify.Spotify -e --accept-package-agreements --accept-source-agreements

# Aguarda alguns segundos para a instalação completar
Start-Sleep -Seconds 5

# Verifica se o executável foi instalado
Write-Host "`n[3/4] Verificando se o Spotify foi instalado..." -ForegroundColor Cyan
$spotifyPath = "$env:APPDATA\Spotify\Spotify.exe"
if (Test-Path $spotifyPath) {
    Write-Host " > Spotify instalado com sucesso." -ForegroundColor Green

    # Abre o Spotify
    Write-Host "`n[4/4] Abrindo o Spotify..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    Start-Process -FilePath $spotifyPath
    Write-Host " > Spotify iniciado." -ForegroundColor Green
} else {
    Write-Host " > ERRO: Spotify não foi encontrado após a instalação." -ForegroundColor Red
}

#endregion Spotify INSTALLER SCRIPT END
