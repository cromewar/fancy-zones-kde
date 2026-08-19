#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Installing KDE FancyZones for Plasma 6 ==="
echo "Project Directory: $PROJECT_DIR"

# 1. Install or update Plasmoid (Top Bar Widget)
echo "Installing Plasma 6 Widget (org.kde.plasma.fancyzones)..."
kpackagetool6 -t Plasma/Applet -u "$PROJECT_DIR/plasmoid" 2>/dev/null || \
kpackagetool6 -t Plasma/Applet -i "$PROJECT_DIR/plasmoid"

# 2. Install or update KWin Script
echo "Installing KWin Snapping Script (fancyzones-kwin)..."
kpackagetool6 -t KWin/Script -u "$PROJECT_DIR/kwin-script" 2>/dev/null || \
kpackagetool6 -t KWin/Script -i "$PROJECT_DIR/kwin-script"

# 3. Enable KWin Script in kwinrc
echo "Enabling FancyZones in KWin configuration..."
kwriteconfig6 --file kwinrc --group Plugins --key fancyzones-kwinEnabled true
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "fancyzones-kwin" 2>/dev/null || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$HOME/.local/share/kwin/scripts/fancyzones-kwin/contents/code/main.js" "fancyzones-kwin" 2>/dev/null || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.start 2>/dev/null || true

# 4. Install Icons & Desktop Launcher
echo "Installing icons and desktop application entry..."
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/scalable/apps"
cp "$PROJECT_DIR/desktop/org.kde.plasma.fancyzones.editor.desktop" "$HOME/.local/share/applications/"
cp "$PROJECT_DIR/icons/fancyzones.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/fancyzones.svg"
gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
kbuildsycoca6 2>/dev/null || true

# 5. Configure Global Shortcuts in kglobalshortcutsrc
echo "Configuring global keyboard shortcuts..."
python3 -c '
import subprocess
shortcuts = {
    "FancyZonesLayout1": ("Meta+Ctrl+Alt+1", "FancyZones: Layout 1 (Priority Grid)"),
    "FancyZonesLayout2": ("Meta+Ctrl+Alt+2", "FancyZones: Layout 2 (3 Columns)"),
    "FancyZonesLayout3": ("Meta+Ctrl+Alt+3", "FancyZones: Layout 3 (4 Columns)"),
    "FancyZonesLayout4": ("Meta+Ctrl+Alt+4", "FancyZones: Layout 4 (Dual 16:9 Split)"),
    "FancyZonesLayout5": ("Meta+Ctrl+Alt+5", "FancyZones: Layout 5 (Master + 4 Flanks)"),
    "FancyZonesLayout6": ("Meta+Ctrl+Alt+6", "FancyZones: Layout 6 (Grid 3x2)"),
    "FancyZonesLayout7": ("Meta+Ctrl+Alt+7", "FancyZones: Layout 7 (Grid 2x2)"),
    "FancyZonesLayout8": ("Meta+Ctrl+Alt+8", "FancyZones: Layout 8 (2 Rows)"),
    "FancyZonesLayout9": ("Meta+Ctrl+Alt+9", "FancyZones: Layout 9 (Focus)"),
    "FancyZonesNextLayout": ("Meta+Ctrl+Alt+Right", "FancyZones: Next Layout"),
    "FancyZonesPrevLayout": ("Meta+Ctrl+Alt+Left", "FancyZones: Previous Layout"),
    "FancyZonesAutoArrange": ("Meta+Ctrl+Alt+A", "FancyZones: Auto-Arrange All Windows"),
    "FancyZonesSnapLeft": ("Meta+Left", "FancyZones: Snap Window Left / Prev Zone"),
    "FancyZonesSnapRight": ("Meta+Right", "FancyZones: Snap Window Right / Next Zone"),
    "FancyZonesSnapUp": ("Meta+Up", "FancyZones: Snap Window Up"),
    "FancyZonesSnapDown": ("Meta+Down", "FancyZones: Snap Window Down"),
    "FancyZonesSnapZone1": ("Meta+Ctrl+1", "FancyZones: Snap to Zone 1"),
    "FancyZonesSnapZone2": ("Meta+Ctrl+2", "FancyZones: Snap to Zone 2"),
    "FancyZonesSnapZone3": ("Meta+Ctrl+3", "FancyZones: Snap to Zone 3"),
    "FancyZonesSnapZone4": ("Meta+Ctrl+4", "FancyZones: Snap to Zone 4"),
    "FancyZonesSnapZone5": ("Meta+Ctrl+5", "FancyZones: Snap to Zone 5"),
    "FancyZonesSnapZone6": ("Meta+Ctrl+6", "FancyZones: Snap to Zone 6"),
    "FancyZonesOpenEditor": ("Meta+Shift+Z", "FancyZones: Open Layout Editor")
}
for name, (key, desc) in shortcuts.items():
    subprocess.run(["kwriteconfig6", "--file", "kglobalshortcutsrc", "--group", "kwin", "--key", name, f"{key},{key},{desc}"], capture_output=True)
' 2>/dev/null || true

# 6. Install & Start Background DBus Service
echo "Setting up systemd user service (fancyzones.service)..."
mkdir -p "$HOME/.config/systemd/user"

UV_EXEC=""
if [ -x "$HOME/.local/bin/uv" ]; then
    UV_EXEC="$HOME/.local/bin/uv run --with PyQt6 python3"
elif command -v uv >/dev/null 2>&1; then
    UV_EXEC="$(command -v uv) run --with PyQt6 python3"
else
    UV_EXEC="python3"
fi

cat << SERVICE_EOF > "$HOME/.config/systemd/user/fancyzones.service"
[Unit]
Description=FancyZones DBus Service for KDE Plasma 6
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=$UV_EXEC $PROJECT_DIR/daemon/fancyzones_service.py
Restart=always
RestartSec=2
Environment=QT_QPA_PLATFORM=wayland

[Install]
WantedBy=graphical-session.target
SERVICE_EOF

systemctl --user daemon-reload
systemctl --user enable --now fancyzones.service

# 7. Add widget to top bar panel
echo "Configuring top bar panel..."
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
var ps = panels();
for (var i = 0; i < ps.length; i++) {
    if (ps[i].location === "top" || ps[i].id === 45) {
        var existing = false;
        var ws = ps[i].widgets();
        for (var j = 0; j < ws.length; j++) {
            if (ws[j].type === "org.kde.plasma.fancyzones") {
                existing = true;
            }
        }
        if (!existing) {
            ps[i].addWidget("org.kde.plasma.fancyzones");
            print("Added FancyZones widget to top bar!");
        }
    }
}
' 2>/dev/null || true

# 9. Reload Plasma Shell to ensure latest widget code is active
systemctl --user restart plasma-plasmashell.service 2>/dev/null || true

echo "=== FancyZones Installation & Setup Complete! ==="
