# Instala o Spotify
winget install --id=Spotify.Spotify -e --accept-package-agreements --accept-source-agreements

# Espera 3 segundos
Start-Sleep -Seconds 3

# Tenta abrir o Spotify
Start-Process "spotify:"
