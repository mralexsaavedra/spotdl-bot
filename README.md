# 🎵 SpotDL Bot

Un bot de Telegram que permite descargar canciones, álbumes y playlists de Spotify utilizando [spotDL](https://github.com/spotDL/spotify-downloader). Gestiona la autenticación con la API de Spotify, guarda el token localmente y responde con los archivos descargados.

---

## 🚀 Características

- 🎷 Descarga canciones, álbumes o playlists de Spotify
- ✅ Autenticación OAuth interactiva
- 🔒 Guarda el token de Spotify de forma persistente
- 🐳 Compatible con Docker
- 🤖 Interfaz vía comandos de Telegram

---

## 📆 Requisitos

- Python 3.10+
- Un bot de Telegram y su token de acceso
- Credenciales de Spotify (Client ID y Secret)

---

## ⚙️ Instalación

### 🔧 Local

```bash
git clone https://github.com/mralexsaavedra/spotdl-bot.git
cd spotdl-bot
pip install -r requirements.txt
cp .env.example .env  # Luego edita con tus datos
python main.py
```

---

### 🐳 Docker

1. Asegúrate de tener Docker instalado.
2. Crea un archivo `.env` con tus credenciales (ver `.env.example`)
3. Lanza el bot:

```bash
docker compose up -d
```

---

## 📜 Licencia

MIT © 2025 [@mralexsaavedra](https://github.com/mralexsaavedra)

---

## 💬 Créditos

Este proyecto usa [spotDL](https://github.com/spotDL/spotify-downloader) como backend de descarga. Gracias a su comunidad por el trabajo increíble.

