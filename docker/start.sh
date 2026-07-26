#!/usr/bin/env bash
# One-shot launcher for the starlab_lab_ops Frappe stack.
# Only entry point you need: `bash docker/start.sh` from the starlab_lab_ops repo root.
# Bootstraps a vendored frappe_docker checkout under .build/ on first run.
set -euo pipefail

DOCKER_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$(cd "$DOCKER_DIR/.." && pwd)"
FD_DIR="$APP_ROOT/.build/frappe_docker"

SITE_NAME="starlab.local"
ADMIN_PASSWORD="admin"
DB_ROOT_PASSWORD="admin123"

if [ ! -d "$FD_DIR/.git" ]; then
  echo "==> Cloning frappe_docker into .build/ (first run only)"
  mkdir -p "$APP_ROOT/.build"
  git clone https://github.com/frappe/frappe_docker.git "$FD_DIR"
fi

if [ ! -f "$DOCKER_DIR/custom.env" ]; then
  echo "==> Creating docker/custom.env from custom.env.example"
  cp "$DOCKER_DIR/custom.env.example" "$DOCKER_DIR/custom.env"
fi

echo "==> Syncing apps.json / custom.env into the frappe_docker checkout"
cp "$DOCKER_DIR/apps.json" "$FD_DIR/apps.json"
cp "$DOCKER_DIR/custom.env" "$FD_DIR/custom.env"

cd "$FD_DIR"

# Windows checkouts of frappe_docker often get CRLF line endings on these
# scripts (via core.autocrlf), which breaks their shebang inside the Linux
# image (`exec ...: no such file or directory`). Normalize defensively.
sed -i 's/\r$//' \
  resources/core/main-entrypoint.sh \
  resources/core/nginx/nginx-entrypoint.sh \
  resources/core/start.sh

if ! docker image inspect starlab-lab-ops:latest >/dev/null 2>&1; then
  echo "==> Building starlab-lab-ops image (first run only, this takes a while)"
  docker build \
    --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
    --build-arg=FRAPPE_BRANCH=version-16 \
    --build-arg=CACHE_BUST="$(date +%s)" \
    --secret=id=apps_json,src=apps.json \
    --tag=starlab-lab-ops:latest \
    --file=images/layered/Containerfile .
else
  echo "==> starlab-lab-ops image already built, skipping build"
  echo "    (edit docker/apps.json and delete the image manually to force a rebuild)"
fi

echo "==> Generating compose.custom.yaml"
docker compose --env-file custom.env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > compose.custom.yaml

echo "==> Starting containers"
docker compose -p frappe -f compose.custom.yaml up -d

echo "==> Waiting for the database to be ready"
until docker compose -p frappe -f compose.custom.yaml exec -T db healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; do
  sleep 3
  echo "    still waiting for db..."
done

echo "==> Waiting for the configurator to finish"
until [ "$(docker compose -p frappe -f compose.custom.yaml ps -a configurator --format '{{.State}}')" = "exited" ]; do
  sleep 2
done

echo "==> Enabling developer mode (needed for Desk-created DocTypes/Workspaces to export as files)"
docker compose -p frappe -f compose.custom.yaml exec -T backend \
  bench set-config -g developer_mode 1

echo "==> Checking if site '$SITE_NAME' already exists"
if docker compose -p frappe -f compose.custom.yaml exec -T backend test -f "sites/$SITE_NAME/site_config.json" 2>/dev/null; then
  echo "    site already exists, skipping creation"
else
  echo "==> Creating site '$SITE_NAME' and installing erpnext + starlab_quality + starlab_lab_ops + starlab_customizations + starlab_integrations"
  # Order matters: starlab_lab_ops.required_apps includes starlab_quality
  # (Test Parameter.metode_uji links to Document Master),
  # starlab_customizations.required_apps includes starlab_lab_ops (Client
  # Inquiry Parameter Detail links to Test Parameter), and
  # starlab_integrations.required_apps includes starlab_lab_ops (the
  # /status-klien portal page queries LHU) -- see each app's hooks.py for
  # the exact reasoning.
  docker compose -p frappe -f compose.custom.yaml exec -T backend \
    bench new-site "$SITE_NAME" \
    --mariadb-user-host-login-scope='%' \
    --db-root-username=root \
    --db-root-password="$DB_ROOT_PASSWORD" \
    --admin-password="$ADMIN_PASSWORD" \
    --install-app erpnext \
    --install-app starlab_quality \
    --install-app starlab_lab_ops \
    --install-app starlab_customizations \
    --install-app starlab_integrations \
    --set-default
fi

echo ""
echo "============================================================"
echo " Ready! Open http://localhost:8080 in your browser."
echo " Login:    Administrator"
echo " Password: $ADMIN_PASSWORD"
echo "============================================================"
