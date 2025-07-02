# 🎵 SpotDL Bot

[![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/mralexsaavedra/spotdl-bot)
[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://hub.docker.com/r/mralexsaavedra/spotdl-bot)
[![Telegram](https://badgen.net/badge/icon/telegram?icon=telegram&label)](https://t.me/spotdl_bot)
![GitHub stars](https://badgen.net/github/stars/mralexsaavedra/spotdl-bot)
![GitHub forks](https://badgen.net/github/forks/mralexsaavedra/spotdl-bot)
![GitHub last-commit](https://badgen.net/github/last-commit/mralexsaavedra/spotdl-bot)
![License](https://badgen.net/github/license/mralexsaavedra/spotdl-bot)

Bot de Telegram que permite descargar canciones, álbumes y playlists completas de Spotify de forma rápida y sencilla, utilizando la potencia de [spotDL](https://github.com/spotDL/spotify-downloader).

---

## 🚀 Funcionalidades

- 🎶 Descargar canciones, álbumes y playlists de Spotify.
- 🔐 Autenticación OAuth interactiva con Spotify.
- 💾 Guardado persistente del token de acceso.
- 🐳 Soporte total para Docker.
- 🤖 Control vía comandos de Telegram.

---

## 📋 Requisitos

- Python 3.10+
- Un bot de Telegram y su token de acceso
- Credenciales de Spotify (Client ID y Secret)

---

## ⚙️ Instalación y ejecución

### 🔧 Local

```bash
git clone https://github.com/mralexsaavedra/spotdl-bot.git
cd spotdl-bot
pip install -r requirements.txt
cp .env.example .env  # Edita .env con tus credenciales
python main.py
```

---

### 🐳 Docker

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Crea un archivo `.env` con las credenciales necesarias.
3. Levanta el contenedor:

```bash
docker compose up -d
```

---

## 🔑 Variables de entorno

| VARIABLE                | OBLIGATORIO  | DESCRIPCIÓN                                                        |
| ----------------------- | ------------ | ------------------------------------------------------------------ |
| TELEGRAM\_TOKEN         | ✅           | Token del bot de Telegram                                          |
| TELEGRAM\_ADMIN         | ✅           | Chat ID del administrador (puede ser múltiple, separado por comas) |
| SPOTIFY\_CLIENT\_ID     | ✅           | Client ID de la aplicación Spotify                                 |
| SPOTIFY\_CLIENT\_SECRET | ✅           | Client Secret de la aplicación Spotify                             |
| SPOTIFY\_REDIRECT\_URI  | ✅           | URI de redirección configurada en la app de Spotify                |
| CONTAINER_NAME          | ✅           | Nombre del contenedor Docker (debe coincidir con docker-compose)   |
| LANGUAGE                | ❌           | Idioma para el bot (por ejemplo: ES, EN). Por defecto ES           |
| TZ                      | ❌           | Zona horaria (ejemplo: Europe/Madrid)                              |

---

## 📝 Licencia

MIT © 2025 [@mralexsaavedra](https://github.com/mralexsaavedra)

---

## 🙌 Créditos

Proyecto basado en [spotDL](https://github.com/spotDL/spotify-downloader). Gracias a la comunidad por este gran software.