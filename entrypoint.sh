#!/bin/sh
set -e

USER_ID=${PUID:-1000}
GROUP_ID=${PGID:-1000}

chown -R ${USER_ID}:${GROUP_ID} /music /cache /logs || true

exec "$@"
