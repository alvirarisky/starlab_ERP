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

# docker/apps.json points our 4 custom apps at separate GitHub branches
# (app-starlab-lab-ops, app-starlab-customizations, app-starlab-quality,
# app-starlab-integrations) instead of `develop` directly -- bench get-app
# (called via apps.json during the image build below) needs each custom app
# as its own standalone repo/branch, but these apps are just subdirectories
# of this monorepo, so they have to be split out. Without re-splitting them
# from the CURRENT develop on every run, those branches silently go stale --
# a `git pull` on this repo never touches them, so a device building the
# image from scratch would install old app code no matter how up to date
# their local checkout is.
#
# REPO_STATE_HASH below is the concatenation of the current HEAD's tree hash
# for exactly the paths bench get-app actually reads (the 4 app dirs +
# apps.json) -- NOT a timestamp. It's identical across runs as long as none
# of those paths changed since the last run, and changes the moment any of
# them do. That single value drives BOTH decisions below: whether the
# subtree branches need re-splitting/pushing at all, and (further down) the
# image's CACHE_BUST -- so an unchanged repo skips the git push entirely
# and lets Docker reuse its build cache instead of re-cloning every app from
# scratch on every single run, while an actual change still forces both a
# fresh push and a fresh build automatically, with nothing to remember to
# do by hand.
REPO_STATE_HASH="$(git -C "$APP_ROOT" rev-parse \
  HEAD:starlab_lab_ops HEAD:starlab_customizations HEAD:starlab_quality HEAD:starlab_integrations HEAD:docker/apps.json \
  | tr '\n' '-')"
SYNC_MARKER="$APP_ROOT/.build/last_synced_apps_state"
mkdir -p "$APP_ROOT/.build"

if [ -f "$SYNC_MARKER" ] && [ "$(cat "$SYNC_MARKER")" = "$REPO_STATE_HASH" ]; then
  echo "==> app-starlab-* branches already match the current repo state, skipping re-sync"
else
  echo "==> Re-syncing app-starlab-* branches with current $(git -C "$APP_ROOT" rev-parse --abbrev-ref HEAD)"
  SUBTREE_PAIRS="starlab_lab_ops:app-starlab-lab-ops starlab_customizations:app-starlab-customizations starlab_quality:app-starlab-quality starlab_integrations:app-starlab-integrations"
  for pair in $SUBTREE_PAIRS; do
    dir="${pair%%:*}"
    branch="${pair##*:}"
    echo "    - $dir -> origin/$branch"
    git -C "$APP_ROOT" branch -D _subtree_sync_tmp >/dev/null 2>&1 || true
    git -C "$APP_ROOT" subtree split --prefix="$dir" -b _subtree_sync_tmp >/dev/null
    git -C "$APP_ROOT" push origin _subtree_sync_tmp:refs/heads/"$branch" --force
    git -C "$APP_ROOT" branch -D _subtree_sync_tmp >/dev/null
  done
  echo "$REPO_STATE_HASH" > "$SYNC_MARKER"
fi

echo "==> Syncing apps.json / custom.env into the frappe_docker checkout"
cp "$DOCKER_DIR/apps.json" "$FD_DIR/apps.json"
cp "$DOCKER_DIR/custom.env" "$FD_DIR/custom.env"

cd "$FD_DIR"

# Windows checkouts of frappe_docker often get CRLF line endings on these
# scripts (via core.autocrlf), which breaks their shebang inside the Linux
# image (`exec ...: no such file or directory`). Normalize defensively.
# Note: -i.bak (suffix attached, no space) is the one in-place form that
# GNU sed (Linux/Windows Git Bash) and BSD sed (macOS) both parse the same
# way -- a bare `-i` needs a following arg on BSD sed, which silently eats
# the script instead and corrupts the whole invocation.
sed -i.bak 's/\r$//' \
  resources/core/main-entrypoint.sh \
  resources/core/nginx/nginx-entrypoint.sh \
  resources/core/start.sh
rm -f resources/core/main-entrypoint.sh.bak \
  resources/core/nginx/nginx-entrypoint.sh.bak \
  resources/core/start.sh.bak

# No more "skip if image already exists" -- that shortcut was exactly how
# devices ended up running stale app code despite `git pull`. Instead,
# CACHE_BUST is now REPO_STATE_HASH (content-based, computed above), not a
# timestamp: identical value in -> identical Docker layer reused, so a run
# where nothing in the 4 app dirs changed hits Docker's build cache and
# finishes in seconds instead of re-cloning every app from scratch. The
# instant any of them change, the hash changes too, which invalidates
# exactly that layer and forces a real rebuild -- automatically, no image
# to remember to `docker rmi` by hand. `docker compose up -d` further down
# recreates any container whose image actually changed.
echo "==> Building starlab-lab-ops image (rebuilds only what actually changed, via content-hash cache busting)"
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --build-arg=CACHE_BUST="$REPO_STATE_HASH" \
  --secret=id=apps_json,src=apps.json \
  --tag=starlab-lab-ops:latest \
  --file=images/layered/Containerfile .

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
  echo "==> Creating site '$SITE_NAME' and installing erpnext + hrms + starlab_quality + starlab_lab_ops + starlab_customizations + starlab_integrations"
  # Order matters: starlab_lab_ops.required_apps includes starlab_quality
  # (Test Parameter.metode_uji links to Document Master),
  # starlab_customizations.required_apps includes starlab_lab_ops (Client
  # Inquiry Parameter Detail links to Test Parameter), and
  # starlab_integrations.required_apps includes starlab_lab_ops (the
  # /status-klien portal page queries LHU) -- see each app's hooks.py for
  # the exact reasoning. hrms (github.com/frappe/hrms) sits before the 4
  # custom apps because role "HR" + Workspace "HR" in starlab_customizations
  # depend on hrms's DocTypes (Leave Application, Payroll Entry, Appraisal,
  # dst) already existing when its fixtures/Custom DocPerm sync.
  docker compose -p frappe -f compose.custom.yaml exec -T backend \
    bench new-site "$SITE_NAME" \
    --mariadb-user-host-login-scope='%' \
    --db-root-username=root \
    --db-root-password="$DB_ROOT_PASSWORD" \
    --admin-password="$ADMIN_PASSWORD" \
    --install-app erpnext \
    --install-app hrms \
    --install-app starlab_quality \
    --install-app starlab_lab_ops \
    --install-app starlab_customizations \
    --install-app starlab_integrations \
    --set-default
fi

echo "==> Running bench migrate (picks up any new Custom DocPerm/Workspace/field fixtures on an already-existing site)"
# The image is rebuilt fresh every run now, but for a site that already
# existed, that alone doesn't apply anything new -- fixtures/schema changes
# baked into the refreshed code only actually reach the site's database via
# migrate. Skipping this would leave the "code is always in sync" guarantee
# above half-true: fresh code, stale database. Safe/idempotent to run even
# right after a brand-new bench new-site (which already migrates once).
docker compose -p frappe -f compose.custom.yaml exec -T backend \
  bench --site "$SITE_NAME" migrate

echo "==> Checking site's installed_apps against app code actually present in this container"
# A site's database remembers which apps are "installed" independently of
# whether their code is still on disk. This drifts whenever a container is
# recreated from an image that was never rebuilt to match (e.g. after
# `bench install-app` was run by hand inside a now-discarded container for
# a quick test, or after docker/apps.json changed without deleting the old
# image) -- every page then 500s with `ModuleNotFoundError`, since the DB
# still lists an app whose package no longer exists. Self-heal it here on
# every run instead of leaving it to reappear and get debugged from scratch
# each time.
docker compose -p frappe -f compose.custom.yaml exec -T backend \
  bash -c 'cd sites && /home/frappe/frappe-bench/env/bin/python3 -' <<'PYEOF'
import importlib.util
import json

import frappe

frappe.init(site="starlab.local")
frappe.connect()

installed = frappe.get_installed_apps()
missing = [a for a in installed if not importlib.util.find_spec(a)]

if missing:
    fixed = [a for a in installed if a not in missing]
    frappe.db.set_global("installed_apps", json.dumps(fixed))
    frappe.db.commit()
    print(f"    WARNING: database listed {missing} as installed, but the code isn't present")
    print("    in this container -- removed from installed_apps so the site loads again.")
    print(f"    If {missing} should really be active: delete the starlab-lab-ops:latest image")
    print("    to force a real rebuild (don't just `bench install-app` inside a running")
    print("    container -- that container is thrown away on restart, the database isn't).")
else:
    print("    OK -- installed_apps matches the app code present in this container.")
PYEOF

echo ""
echo "============================================================"
echo " Ready! Open http://localhost:8080 in your browser."
echo " Login:    Administrator"
echo " Password: $ADMIN_PASSWORD"
echo "============================================================"
