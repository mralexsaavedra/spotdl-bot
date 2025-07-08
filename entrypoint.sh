#!/bin/sh
set -e

# Cambia permisos de carpetas si es necesario
chown -R appuser:appuser /music /cache /logs || true

exec "$@"
