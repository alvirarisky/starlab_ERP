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

# docker/apps.json pins erpnext/hrms to real, fixed release tags (see
# comments in that file) -- those two are fetched from a real git remote and
# don't need anything special. Our own 4 apps are different: they're just
# subdirectories of THIS monorepo with no meaningful separate remote of
# their own, but `bench get-app` (called during the image build below, via
# apps.json) only accepts a git URL or a local git-repo-root path -- a bare
# subfolder of a bigger repo doesn't qualify.
#
# This used to be solved by `git subtree split`-ing each app subfolder and
# force-pushing it to its own throwaway branch on GitHub on every run, just
# so `bench get-app <url>` had something to clone. That meant every run of
# this script could push to the remote repo -- not something a local dev
# script should ever silently do -- and made testing a change slow (push,
# then wait for a full image rebuild to see if it worked).
#
# Fixed the same way this project's own CI already solves the identical
# problem (see .github/workflows/ci.yml, "Turn app subfolders into
# standalone git repos"): copy the 4 app folders into a local build context
# and git-init each one INSIDE the image build itself (docker/Containerfile
# does the git-init step) -- bench get-app then clones from that local path.
# Nothing is ever pushed anywhere, and Docker's own content-addressed build
# cache handles staleness correctly on its own (a COPY layer is invalidated
# the instant the copied files differ, including uncommitted changes -- no
# manual cache-busting hash needed for this part, unlike the old subtree
# branches which Docker had no way to know had gone stale).
echo "==> Refreshing local build context for starlab_customizations/starlab_integrations/starlab_lab_ops/starlab_quality"
BUILD_CTX_APPS="$APP_ROOT/.build/build_context_apps"
rm -rf "$BUILD_CTX_APPS"
mkdir -p "$BUILD_CTX_APPS"
for app in starlab_customizations starlab_integrations starlab_lab_ops starlab_quality; do
  cp -r "$APP_ROOT/$app" "$BUILD_CTX_APPS/$app"
done
find "$BUILD_CTX_APPS" -type d -name "__pycache__" -prune -exec rm -rf {} +

# apps.json fed to the build (via --secret below) is generated fresh each
# run: erpnext/hrms entries copied verbatim from the tracked docker/apps.json
# (real URL + pinned tag), plus the 4 local paths the Containerfile COPYs
# the build context into (/opt/starlab_apps/<name> -- see docker/Containerfile).
# The tracked docker/apps.json itself no longer lists the 4 apps at all --
# there is no meaningful remote URL for them anymore, so listing one there
# would be misleading.
GENERATED_APPS_JSON="$APP_ROOT/.build/generated_apps.json"
node -e '
const fs = require("fs");
const [src, dst] = process.argv.slice(1);
const apps = JSON.parse(fs.readFileSync(src, "utf8"));
for (const name of ["starlab_customizations", "starlab_integrations", "starlab_lab_ops", "starlab_quality"]) {
  apps.push({ url: `/opt/starlab_apps/${name}` });
}
fs.writeFileSync(dst, JSON.stringify(apps, null, 2));
' "$DOCKER_DIR/apps.json" "$GENERATED_APPS_JSON"

echo "==> Syncing custom.env into the frappe_docker checkout"
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

# REPO_STATE_HASH is a content hash of what actually got copied into
# BUILD_CTX_APPS above -- used further down to decide whether `bench
# migrate` needs to re-run against the running site. It intentionally
# reflects the current WORKING TREE (including uncommitted changes), not
# just the last commit, so this stays correct even mid-edit.
#
# No CACHE_BUST build-arg needed anymore: Docker/BuildKit's own build cache
# is content-addressed, so the `COPY --from=starlab_apps` layer in
# docker/Containerfile (and everything after it) is invalidated automatically
# the instant any of these files actually differ -- no manual hash-forcing
# required the way the old remote-branch-based fetch needed. A run where
# nothing changed hits the build cache and finishes in seconds; an actual
# change invalidates exactly the right layers.
REPO_STATE_HASH="$(find "$BUILD_CTX_APPS" -type f -exec sha256sum {} \; | sort | sha256sum | cut -d' ' -f1)"

echo "==> Building starlab-lab-ops image (rebuilds only what actually changed, via Docker's own content-addressed cache)"
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=v16.29.0 \
  --secret=id=apps_json,src="$GENERATED_APPS_JSON" \
  --build-context=starlab_apps="$BUILD_CTX_APPS" \
  --tag=starlab-lab-ops:latest \
  --file="$DOCKER_DIR/Containerfile" .

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

MIGRATE_MARKER="$APP_ROOT/.build/last_migrated_apps_state"

echo "==> Checking if site '$SITE_NAME' already exists"
if docker compose -p frappe -f compose.custom.yaml exec -T backend test -f "sites/$SITE_NAME/site_config.json" 2>/dev/null; then
  echo "    site already exists, skipping creation"

  # bench migrate re-syncs EVERY DocType across EVERY installed app (frappe +
  # erpnext + hrms + our 4 apps -- several hundred DocTypes combined) on
  # every single invocation, whether or not anything actually changed. That
  # made it the real bottleneck once it started running unconditionally on
  # every run -- worse than the image build itself, which Docker's own build
  # cache already makes near-instant when nothing changed. Same fix, same
  # REPO_STATE_HASH (content hash of the 4 app dirs' working tree, computed
  # above): only actually run it when the repo state moved since the last
  # time it ran.
  if [ -f "$MIGRATE_MARKER" ] && [ "$(cat "$MIGRATE_MARKER")" = "$REPO_STATE_HASH" ]; then
    echo "==> Site already migrated for the current repo state, skipping bench migrate"
  else
    echo "==> Running bench migrate (repo state changed since the last migrate)"
    docker compose -p frappe -f compose.custom.yaml exec -T backend \
      bench --site "$SITE_NAME" migrate
    echo "$REPO_STATE_HASH" > "$MIGRATE_MARKER"
  fi
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
  # Each --install-app above already runs its own migrate-equivalent pass,
  # but those happen mid-sequence -- an app's after_migrate hook can fire
  # before a LATER app in this same list has synced its DocTypes yet (hit
  # this for real: starlab_customizations's after_migrate builds a sidebar
  # linking to hrms DocTypes, and even though hrms is installed earlier in
  # this list, one Mac run crashed here because they weren't visible yet at
  # that exact moment -- see the defensive fix in install.py). One clean
  # final migrate once every app is actually in place is cheap here (site
  # creation is a one-time event, not the repeated dev-loop case the
  # skip-if-unchanged logic above is optimizing for) and guarantees nothing
  # is left half-applied.
  docker compose -p frappe -f compose.custom.yaml exec -T backend \
    bench --site "$SITE_NAME" migrate
  echo "$REPO_STATE_HASH" > "$MIGRATE_MARKER"
fi

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
