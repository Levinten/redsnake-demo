#!/bin/bash
set -e

# ── SSH key setup ──────────────────────────────────────────────
# If an SSH key is mounted, configure SSH for git access.
if [ -f "$HOME/.ssh/id_rsa" ]; then
    chmod 600 "$HOME/.ssh/id_rsa" 2>/dev/null || true
    # Disable strict host key checking to avoid interactive prompts
    if [ ! -f "$HOME/.ssh/config" ]; then
        cat > "$HOME/.ssh/config" <<EOF
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
EOF
        chmod 600 "$HOME/.ssh/config"
    fi
    echo "[entrypoint] SSH key detected."
fi

# ── Git repository clone / pull ────────────────────────────────
if [ -n "$GIT_REPO_URL" ]; then
    GIT_BRANCH="${GIT_BRANCH:-main}"
    REPO_DIR="/app/repo"

    if [ -d "$REPO_DIR/.git" ]; then
        echo "[entrypoint] Pulling latest changes (branch: $GIT_BRANCH)..."
        cd "$REPO_DIR" && git fetch origin && git reset --hard "origin/$GIT_BRANCH"
        cd /app
    else
        echo "[entrypoint] Cloning repository (branch: $GIT_BRANCH)..."
        git clone --branch "$GIT_BRANCH" --single-branch "$GIT_REPO_URL" "$REPO_DIR"
    fi
    echo "[entrypoint] Repository ready at $REPO_DIR"
else
    echo "[entrypoint] No GIT_REPO_URL set — skipping repository sync."
fi

# ── Hand off to the container command ──────────────────────────
exec "$@"
