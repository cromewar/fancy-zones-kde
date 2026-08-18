#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Updating KDE FancyZones for Plasma 6 ==="
echo "Project Directory: $PROJECT_DIR"

# 1. Git pull if inside a git repository
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Pulling latest changes from git repository..."
    cd "$PROJECT_DIR"
    git pull --rebase 2>/dev/null || git pull 2>/dev/null || true
fi

# 2. Upgrade KWin script, Plasmoid widget, desktop files, shortcuts, and DBus service
bash "$PROJECT_DIR/bin/install.sh"

# 3. Restart FancyZones background service
systemctl --user restart fancyzones.service 2>/dev/null || true

echo "=== KDE FancyZones Successfully Updated! ==="
