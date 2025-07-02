# 🎵 SpotDL Bot

[![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/mralexsaavedra/spotdl-bot)
[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://hub.docker.com/r/mralexsaavedra/spotdl-bot)
[![Telegram](https://badgen.net/badge/icon/telegram?icon=telegram&label)](https://t.me/spotdl_bot)
![GitHub stars](https://badgen.net/github/stars/mralexsaavedra/spotdl-bot)
![GitHub forks](https://badgen.net/github/forks/mralexsaavedra/spotdl-bot)
![GitHub last-commit](https://badgen.net/github/last-commit/mralexsaavedra/spotdl-bot)
![License](https://badgen.net/github/license/mralexsaavedra/spotdl-bot)
[![Version](https://img.shields.io/github/v/release/mralexsaavedra/spotdl-bot)](https://github.com/mralexsaavedra/spotdl-bot/releases)

Bot de Telegram que permite descargar canciones, álbumes y playlists completas de Spotify de forma rápida y sencilla, utilizando la potencia de [spotDL](https://github.com/spotDL/spotify-downloader).

---

## 🚀 Funcionalidades

- 🎶 Descargar canciones, álbumes y playlists de Spotify.
- 🔐 Autenticación OAuth interactiva con Spotify.
- 💾 Guarda el token de Spotify de forma persistente.
- 🐳 Compatible con Docker.
- 🤖 Control vía comandos de Telegram.

---

## 📋 Requisitos

- Python 3.10+
- [Un bot de Telegram y su token de acceso](#telegram-bot-token)
- [Chat ID de Telegram para el administrador del bot](#chat-id-telegram)
- [Credenciales de Spotify (Client ID y Secret)](#credenciales-spotify)
- [URI de redirección para Spotify (Spotify Redirect URI)](#spotify-redirect-uri)

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

<a id="telegram-bot-token"></a>
### 🤖 Cómo crear un bot de Telegram y obtener su token

Sigue esta [guía oficial de Telegram](https://core.telegram.org/bots#6-botfather) para crear un bot y obtener el token.

---

<a id="chat-id-telegram"></a>
### 📌 ¿Cómo obtener el Chat ID de Telegram?

El **Chat ID** es un identificador numérico único para tu usuario o grupo en Telegram, necesario para que el bot sepa a quién enviar mensajes o aceptar comandos.

Para obtener tu Chat ID personal, puedes hablar con el bot [@MissRose_bot](https://t.me/MissRose_bot) y escribir el comando `/id`.  
El bot te responderá con tu Chat ID, que deberás usar como valor para la variable `TELEGRAM_ADMIN`.

Para más información sobre bots y tokens, consulta la documentación oficial: [https://core.telegram.org/bots#6-botfather](https://core.telegram.org/bots#6-botfather)

---

<a id="credenciales-spotify"></a>
### 🎵 Credenciales de Spotify (Client ID y Client Secret)

Para que el bot pueda acceder a la API de Spotify y descargar canciones, álbumes o playlists, necesitas crear una aplicación en el **Dashboard de Desarrolladores de Spotify** y obtener dos credenciales:

- **Client ID**: Identificador público de tu aplicación.  
- **Client Secret**: Clave privada que permite autenticar tu aplicación.

Estas credenciales permiten al bot autenticar solicitudes y acceder a los datos de Spotify mediante OAuth.

#### Cómo obtener las credenciales de Spotify:

1. Accede al [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).  
2. Inicia sesión con tu cuenta de Spotify.  
3. Crea una nueva aplicación haciendo clic en **"Create an App"**.  
4. Dale un nombre y una descripción a tu aplicación.  
<a id="spotify-redirect-uri"></a>
5. En la configuración de la aplicación, añade en **Redirect URIs** la URL que usarás para la autenticación, por ejemplo, http://127.0.0.1:9900/.
6. Guarda los cambios.  
7. Copia el **Client ID** y el **Client Secret** para usarlos en las variables de entorno.

---

## 📋 Comandos disponibles

| Comando           | Descripción                          |
|-------------------|------------------------------------|
| `/start`          | Mostrar menú inicial                |
| `/authorize`      | Autorizar acceso a Spotify          |
| `/download`       | Descargar canción/álbum/playlist    |
| `/downloadliked`  | Descargar canciones favoritas    |
| `/version`        | Mostrar versión del bot             |
| `/donate`         | Información para donar              |

---

## 🐳 Instalación con Docker

Puedes ejecutar el bot fácilmente usando Docker o Docker Compose.
A continuación, te explico ambas opciones.

### ▶️ Opción 1: Usar docker run

```bash
docker run -d --name spotdl-bot \
  -e TELEGRAM_TOKEN="tu_token" \
  -e TELEGRAM_ADMIN="tu_chat_id" \
  -e SPOTIFY_CLIENT_ID="tu_client_id" \
  -e SPOTIFY_CLIENT_SECRET="tu_client_secret" \
  -e SPOTIFY_REDIRECT_URI="tu_redirect_uri" \
  -e LANGUAGE="es" \
  mralexsaavedra/spotdl-bot
```

### ⚙️ Opción 2: Usar docker-compose

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Crea un archivo `.env` con las credenciales necesarias.
3. Crea el archivo `docker-compose.yml`:

```yaml
version: "3.8"

services:
  spotdl-bot:
    image: mralexsaavedra/spotdl-bot
    container_name: spotdl-bot
    env_file: .env
    restart: unless-stopped

```

4. Levanta el contenedor:

```bash
docker compose up -d
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Abre un issue o pull request para mejorar el proyecto.

---

## 📝 Licencia

MIT © 2025 [@mralexsaavedra](https://github.com/mralexsaavedra)

---

## 🙌 Créditos

Proyecto basado en [spotDL](https://github.com/spotDL/spotify-downloader). Gracias a la comunidad por este gran software.

---

Hecho con ❤️ por [mralexsaavedra](https://mralexsaavedra.com)