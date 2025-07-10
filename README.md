# 🎵 SpotDL Bot

[![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/mralexsaavedra/spotdl-bot)
[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://hub.docker.com/r/mralexandersaavedra/spotdl-bot)
![GitHub stars](https://badgen.net/github/stars/mralexsaavedra/spotdl-bot)
![GitHub forks](https://badgen.net/github/forks/mralexsaavedra/spotdl-bot)
![GitHub last-commit](https://badgen.net/github/last-commit/mralexsaavedra/spotdl-bot)
![License](https://badgen.net/github/license/mralexsaavedra/spotdl-bot)
[![Version](https://img.shields.io/github/v/release/mralexsaavedra/spotdl-bot)](https://github.com/mralexsaavedra/spotdl-bot/releases)
[![Donar](https://img.shields.io/badge/Donar-Coffee%20%F0%9F%92%B0-orange)](https://www.buymeacoffee.com/mralexsaavedra)
[![Web personal](https://img.shields.io/badge/Web-mralexsaavedra.com-blue)](https://mralexsaavedra.com)

Bot de Telegram que permite descargar canciones, álbumes y playlists completas de Spotify de forma rápida y sencilla, utilizando la potencia de [spotDL](https://github.com/spotDL/spotify-downloader).

---

## 📑 Tabla de Contenidos

- [🎵 SpotDL Bot](#-spotdl-bot)
  - [📑 Tabla de Contenidos](#-tabla-de-contenidos)
  - [🚀 Funcionalidades](#-funcionalidades)
  - [📋 Requisitos](#-requisitos)
  - [🔑 Variables de entorno](#-variables-de-entorno)
    - [🤖 Cómo crear un bot de Telegram y obtener su token](#-cómo-crear-un-bot-de-telegram-y-obtener-su-token)
    - [📌 ¿Cómo obtener el Chat ID de Telegram?](#-cómo-obtener-el-chat-id-de-telegram)
    - [🎵 Credenciales de Spotify (Client ID y Client Secret)](#-credenciales-de-spotify-client-id-y-client-secret)
      - [Cómo obtener las credenciales de Spotify:](#cómo-obtener-las-credenciales-de-spotify)
  - [📋 Comandos disponibles](#-comandos-disponibles)
  - [🐳 Instalación con Docker](#-instalación-con-docker)
    - [▶️ Opción 1: Usar docker run](#️-opción-1-usar-docker-run)
    - [⚙️ Opción 2: Usar docker-compose](#️-opción-2-usar-docker-compose)
  - [⚠️ Límites de uso de la API de Spotify (Rate Limits)](#️-límites-de-uso-de-la-api-de-spotify-rate-limits)
  - [🛠️ Funcionamiento interno: SpotifyDownloader](#️-funcionamiento-interno-spotifydownloader)
  - [🤝 Contribuciones](#-contribuciones)
  - [📝 Licencia](#-licencia)
  - [🙌 Créditos](#-créditos)

---

## 🚀 Funcionalidades

- 🎶 **Descarga avanzada**: Descarga canciones, álbumes, playlists y artistas completos de Spotify.
- 🗂️ **Organización automática**: Estructura las descargas en carpetas por artista, álbum y playlist.
- 🖼️ **Portadas automáticas**: Descarga y guarda las portadas de artistas y playlists.
- 📄 **Listas M3U para playlists**: Genera archivos M3U compatibles con Jellyfin, Navidrome y otros servidores.
- 🔄 **Sincronización inteligente**: Mantén tu biblioteca local siempre actualizada y limpia con el sistema de sincronización.
- 🌍 **Multi-idioma**: Interfaz y menús disponibles en varios idiomas.
- 🐳 **Compatible con Docker**: Fácil despliegue y actualización con Docker o Docker Compose.
- 🤖 **Control total por Telegram**: Gestiona todas las descargas y sincronizaciones desde tu móvil o PC.
- 📝 **Logs detallados**: Consulta los registros de actividad y errores en la carpeta `logs/`.
- 🔒 **Privacidad**: Todo el procesamiento y almacenamiento es local, sin servicios de terceros.

---

## 📋 Requisitos

- Python 3.10+
- [Un bot de Telegram y su token de acceso](#-cómo-crear-un-bot-de-telegram-y-obtener-su-token)
- [Chat ID de Telegram para el administrador del bot](#-cómo-obtener-el-chat-id-de-telegram)
- [Credenciales de Spotify (Client ID y Secret)](#-credenciales-de-spotify-client-id-y-client-secret)
- [URI de redirección para Spotify (Spotify Redirect URI)](#spotify-redirect-uri)

---

## 🔑 Variables de entorno

| VARIABLE                | OBLIGATORIO  | DESCRIPCIÓN                                                                |
| ----------------------- | ------------ | ---------------------------------------------------------------------------|
| TELEGRAM\_TOKEN         | ✅           | Token del bot de Telegram                                                  |
| TELEGRAM\_ADMIN         | ✅           | Chat ID del administrador (puede ser múltiple, separado por comas)         |
| SPOTIFY\_CLIENT\_ID     | ✅           | Client ID de la aplicación Spotify                                         |
| SPOTIFY\_CLIENT\_SECRET | ✅           | Client Secret de la aplicación Spotify                                     |
| SPOTIFY\_REDIRECT\_URI  | ✅           | URI de redirección configurada en la app de Spotify                        |
| PUID                    | ❌           | UID del usuario para los permisos del contenedor Docker (opcional)         |
| PGID                    | ❌           | GID del grupo para los permisos del contenedor Docker (opcional)           |
| TZ                      | ❌           | Zona horaria (ejemplo: Europe/Madrid)                                      |
| LANGUAGE                | ❌           | Idioma para el bot (por ejemplo: ES, EN). Por defecto ES                   |

---

### 🤖 Cómo crear un bot de Telegram y obtener su token

Sigue esta [guía oficial de Telegram](https://core.telegram.org/bots#6-botfather) para crear un bot y obtener el token.

---

### 📌 ¿Cómo obtener el Chat ID de Telegram?

El **Chat ID** es un identificador numérico único para tu usuario o grupo en Telegram, necesario para que el bot sepa a quién enviar mensajes o aceptar comandos.

Para obtener tu Chat ID personal, puedes hablar con el bot [@MissRose_bot](https://t.me/MissRose_bot) y escribir el comando `/id`.  
El bot te responderá con tu Chat ID, que deberás usar como valor para la variable `TELEGRAM_ADMIN`.

Para más información sobre bots y tokens, consulta la documentación oficial: [https://core.telegram.org/bots#6-botfather](https://core.telegram.org/bots#6-botfather)

---

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

| Comando                         | Descripción                                                                                          |
|---------------------------------|------------------------------------------------------------------------------------------------------|
| `/start`                        | Mostrar menú inicial                                                                                 |
| `/download`                     | Descargar canción/álbum/playlist                                                                     |
| `/downloadsavedsongs`           | Descargar tus canciones guardadas                                                                    |
| `/downloadsavedalbums`          | Descargar tus álbumes guardados                                                                      |
| `/downloadsavedplaylists`       | Descargar tus playlists guardadas                                                                    |
| `/downloaduserplaylists`        | Descargar tus playlists creadas                                                                      |
| `/downloaduserfollowedartists`  | Descargar los artistas que sigues                                                                    |
| `/sync`                         | Sincronizar tu biblioteca                                                                            |
| `/version`                      | Mostrar versión del bot                                                                              |
| `/donate`                       | Información para donar                                                                               |


---

## 🐳 Instalación con Docker

Puedes ejecutar el bot fácilmente usando Docker o Docker Compose.

### ▶️ Opción 1: Usar docker run

```bash
docker run -d --name spotdl-bot \
  -e TELEGRAM_TOKEN="tu_token" \
  -e TELEGRAM_ADMIN="tu_chat_id" \
  -e SPOTIFY_CLIENT_ID="tu_client_id" \
  -e SPOTIFY_CLIENT_SECRET="tu_client_secret" \
  -e SPOTIFY_REDIRECT_URI="tu_redirect_uri" \
  -e LANGUAGE="es" \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Europe/Madrid \
  -v $(pwd)/music:/music \
  -v $(pwd)/cache:/cache \
  -v $(pwd)/logs:/logs \
  mralexandersaavedra/spotdl-bot
```

> **Nota:** Asegúrate de crear los directorios `music`, `cache` y `logs` en tu máquina antes de ejecutar el comando, o Docker los creará vacíos.

### ⚙️ Opción 2: Usar docker-compose

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Crea un archivo `.env` con las credenciales necesarias (puedes usar `.env.example` como plantilla).
3. Crea el archivo `docker-compose.yml`:

```yaml
services:
  spotdl-bot:
    image: mralexsaavedra/spotdl-bot:latest
    container_name: spotdl-bot
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Madrid
      - LANGUAGE=ES # IDIOMAS DISPONIBLES: ES, EN
    env_file:
      - .env
    volumes:
      - ./music:/music # CAMBIA ESTA RUTA A TU DIRECTORIO DE MÚSICA
      - ./cache:/cache # CAMBIA ESTA RUTA AL DIRECTORIO QUE QUIERAS PARA LA CACHE
      - ./logs:/logs # CAMBIA ESTA RUTA AL DIRECTORIO QUE QUIERAS PARA LOS LOGS
    restart: unless-stopped
```

Puedes encontrar este archivo y personalizarlo en el repositorio: [`docker-compose.yml`](./docker-compose.yml)

4. Levanta el contenedor:

```bash
docker compose up -d
```

> **Consejo:** Puedes personalizar los volúmenes y la configuración en el archivo `.env` y `docker-compose.yml` según tus necesidades.

---

## ⚠️ Límites de uso de la API de Spotify (Rate Limits)

Este bot utiliza la API oficial de Spotify, la cual puede imponer límites de uso (rate limits) si se realizan demasiadas solicitudes en poco tiempo. Si esto ocurre, el bot puede mostrar mensajes de error o fallar temporalmente al descargar contenido. Para más información sobre los límites de la API de Spotify, consulta la documentación oficial:

- [Spotify API Rate Limits](https://developer.spotify.com/documentation/web-api/concepts/rate-limits)

---

## 🛠️ Funcionamiento interno: SpotifyDownloader

La clase `SpotifyDownloader` es el núcleo del bot y se encarga de gestionar todas las operaciones relacionadas con la descarga y sincronización de contenido de Spotify. Sus principales responsabilidades son:

- **Descarga de contenido**: Permite descargar canciones, álbumes, playlists y artistas usando SpotDL, gestionando los patrones de salida y la estructura de carpetas.
  > La estructura de carpetas es automática: las playlists se guardan en `Playlists/{nombre_playlist}/`, y los álbumes y canciones sueltas en `{nombre_artista}/{nombre_album}/`. Así, tu música queda organizada y lista para usar en cualquier reproductor o servidor de música.
- **Sincronización**: Mantiene un archivo de sincronización para que puedas actualizar tu biblioteca local según los cambios en tus playlists, álbumes o canciones guardadas.
  > El archivo de sincronización se guarda en `cache/sync.spotdl` y almacena el estado de tus descargas para facilitar futuras actualizaciones o limpiezas automáticas. Si en el futuro quieres eliminar una sincronización, solo tienes que borrar la query correspondiente de este fichero.
- **Manejo de imágenes**: Descarga y guarda automáticamente las portadas de artistas y playlists en sus carpetas correspondientes.
- **Generación de archivos M3U**: Crea listas de reproducción M3U8 agrupando las canciones por playlist.
  > Los archivos M3U se generan únicamente para las playlists y permiten que servicios externos como Jellyfin o Navidrome reconozcan automáticamente las listas de reproducción descargadas.
- **Gestión de errores y logs**: Implementa un sistema robusto de logging y manejo de errores para operaciones de archivos, red y API.
  > Los logs de actividad y errores se guardan en la carpeta `logs/` del proyecto para su consulta y diagnóstico.
- **Internacionalización (i18n)**: Todos los mensajes y menús del bot están preparados para varios idiomas.
- **Integración con Telegram**: Todos los métodos están diseñados para interactuar con el bot de Telegram, enviando mensajes de estado y errores al usuario.

La clase está pensada para ser robusta, fácil de mantener y extensible. Puedes consultar el código fuente en [`spotifyDownloader/__init__.py`](./spotifyDownloader/__init__.py) para más detalles sobre cada método y su funcionamiento.

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