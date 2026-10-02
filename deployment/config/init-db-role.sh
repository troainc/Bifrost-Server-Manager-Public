#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ! -r "${BIFROST_APP_PASSWORD_FILE:-}" ]]; then
  echo "BIFROST_APP_PASSWORD_FILE must reference a readable Compose secret." >&2
  exit 1
fi
BIFROST_APP_PASSWORD="$(< "$BIFROST_APP_PASSWORD_FILE")"
if [[ ${#BIFROST_APP_PASSWORD} -lt 32 ]]; then
  echo "The Bifrost database app password must contain at least 32 characters." >&2
  exit 1
fi
export BIFROST_APP_PASSWORD
psql --set ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --file /etc/10-bifrost-app-role.sql
unset BIFROST_APP_PASSWORD
