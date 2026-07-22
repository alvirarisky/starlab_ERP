#!/usr/bin/env bash
# Stops the starlab_lab_ops stack (containers stay removed, data volumes are kept).
set -euo pipefail

DOCKER_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$(cd "$DOCKER_DIR/.." && pwd)"
FD_DIR="$APP_ROOT/.build/frappe_docker"

cd "$FD_DIR"
docker compose -p frappe -f compose.custom.yaml down
