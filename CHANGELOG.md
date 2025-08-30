# Changelog

Todas las versiones y cambios importantes del proyecto.

## v0.1.5
- Añadido workflow para releases automáticas.
- Mejoras en la gestión de versiones y releases.
- Publicación automática de imágenes Docker al crear una release.
- Extracción de versión desde config.py para control de releases.
- Integración con CHANGELOG.md para el cuerpo de la release.
- Corrección de errores en workflows para primer commit y permisos.

## v0.1.6
- Mejoras en las claves de traducción y descripciones de comandos
- Limpieza de comandos obsoletos en menús y archivos de traducción
- Mejoras menores de UI/UX en el bot de Telegram

## v0.1.7
- Corrección en la lógica de actualización del archivo de sincronización para evitar sobrescritura de datos
- Refactor del método sync para mayor robustez y claridad
- Mejoras menores en la gestión de queries y sincronización

## v0.1.8
- Actualizado a la última versión de spotdl (v4.4.0)

## v0.1.9
- Corrección en la extracción de metadatos del artista

## v0.1.10
- Se ha eliminado el archivo Song para importarlo directamente de la libreria spotdl

## v0.1.11
- Migración de config.py a settings.py y renombrado de la carpeta a settings/
- Actualización de todos los imports para usar settings.settings
- Corrección en el entrypoint para generación automática de config.json de SpotDL
- Documentación mejorada sobre el volumen de configuración y ubicación de config.json
- Tip añadido en el README para acelerar descargas desactivando lyrics_providers

## v0.1.12
- Actualizado a la última versión de spotdl (v4.4.1)

