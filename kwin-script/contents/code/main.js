/**
 * KDE FancyZones - KWin Snapping Engine & Layout Manager (Plasma 6)
 */

var DEBUG = true;

function log(msg) {
    if (DEBUG) {
        print("[FancyZones-KWin] " + msg);
    }
}

// Built-in curated layouts (optimized for 32:9 Super Ultrawide, 21:9 Ultrawide, and Standard monitors)
var BUILTIN_LAYOUTS = [
    {
        id: "priority-grid",
        name: "Priority Grid",
        shortcut: 1,
        zones: [
            [0.0, 0.0, 0.25, 1.0],      // 1: Left column (1280x1440)
            [0.25, 0.0, 0.50, 1.0],     // 2: Center Main Workspace (2560x1440)
            [0.75, 0.0, 0.25, 1.0]      // 3: Right column (1280x1440)
        ]
    },
    {
        id: "cols-3",
        name: "3 Columns",
        shortcut: 2,
        zones: [
            [0.0, 0.0, 0.3333, 1.0],    // 1: Left 33.3% (1706x1440)
            [0.3333, 0.0, 0.3334, 1.0], // 2: Center 33.4% (1707x1440)
            [0.6667, 0.0, 0.3333, 1.0]  // 3: Right 33.3% (1706x1440)
        ]
    },
    {
        id: "cols-4",
        name: "4 Columns",
        shortcut: 3,
        zones: [
            [0.0, 0.0, 0.25, 1.0],      // 1: 25% (1280x1440)
            [0.25, 0.0, 0.25, 1.0],     // 2: 25% (1280x1440)
            [0.50, 0.0, 0.25, 1.0],     // 3: 25% (1280x1440)
            [0.75, 0.0, 0.25, 1.0]      // 4: 25% (1280x1440)
        ]
    },
    {
        id: "dual-split",
        name: "Dual 16:9 Split",
        shortcut: 4,
        zones: [
            [0.0, 0.0, 0.50, 1.0],      // 1: Left 50% (2560x1440)
            [0.50, 0.0, 0.50, 1.0]      // 2: Right 50% (2560x1440)
        ]
    },
    {
        id: "ultrawide-master-4",
        name: "Master + 4 Flanks",
        shortcut: 5,
        zones: [
            [0.25, 0.0, 0.50, 1.0],     // 1: Center Master (2560x1440)
            [0.0, 0.0, 0.25, 0.50],     // 2: Top-Left (1280x720)
            [0.0, 0.50, 0.25, 0.50],    // 3: Bottom-Left (1280x720)
            [0.75, 0.0, 0.25, 0.50],    // 4: Top-Right (1280x720)
            [0.75, 0.50, 0.25, 0.50]    // 5: Bottom-Right (1280x720)
        ]
    },
    {
        id: "grid-3x2",
        name: "Grid 3x2",
        shortcut: 6,
        zones: [
            [0.0, 0.0, 0.3333, 0.50],   // 1: Top-Left (1706x720)
            [0.3333, 0.0, 0.3334, 0.50],// 2: Top-Center (1707x720)
            [0.6667, 0.0, 0.3333, 0.50],// 3: Top-Right (1706x720)
            [0.0, 0.50, 0.3333, 0.50],  // 4: Bottom-Left (1706x720)
            [0.3333, 0.50, 0.3334, 0.50],// 5: Bottom-Center (1707x720)
            [0.6667, 0.50, 0.3333, 0.50] // 6: Bottom-Right (1706x720)
        ]
    },
    {
        id: "grid-2x2",
        name: "Grid 2x2",
        shortcut: 7,
        zones: [
            [0.0, 0.0, 0.50, 0.50],     // 1: Top-Left (2560x720)
            [0.50, 0.0, 0.50, 0.50],    // 2: Top-Right (2560x720)
            [0.0, 0.50, 0.50, 0.50],    // 3: Bottom-Left (2560x720)
            [0.50, 0.50, 0.50, 0.50]    // 4: Bottom-Right (2560x720)
        ]
    },
    {
        id: "rows-2",
        name: "2 Rows",
        shortcut: 8,
        zones: [
            [0.0, 0.0, 1.0, 0.50],      // 1: Top Half (5120x720)
            [0.0, 0.50, 1.0, 0.50]      // 2: Bottom Half (5120x720)
        ]
    },
    {
        id: "focus",
        name: "Focus Zone",
        shortcut: 9,
        zones: [
            [0.20, 0.08, 0.60, 0.84]    // 1: Center Focus Canvas
        ]
    }
];

var state = {
    settings: {
        gap: 8,
        margin: 8
    },
    activeLayouts: {},
    layouts: BUILTIN_LAYOUTS
};

// Compute pixel bounding box for a zone on a given screen work area
function computeZoneRect(zoneNorm, workArea, gap, margin) {
    var sx = workArea.x + margin;
    var sy = workArea.y + margin;
    var sw = workArea.width - (2 * margin);
    var sh = workArea.height - (2 * margin);

    var zx = zoneNorm[0];
    var zy = zoneNorm[1];
    var zw = zoneNorm[2];
    var zh = zoneNorm[3];

    var px = sx + Math.round(zx * sw);
    var py = sy + Math.round(zy * sh);
    var pw = Math.round(zw * sw);
    var ph = Math.round(zh * sh);

    var halfGap = Math.floor(gap / 2);

    var fx = px + (zx > 0.001 ? halfGap : 0);
    var fy = py + (zy > 0.001 ? halfGap : 0);
    var fw = pw - (zx > 0.001 ? halfGap : 0) - ((zx + zw) < 0.999 ? halfGap : 0);
    var fh = ph - (zy > 0.001 ? halfGap : 0) - ((zy + zh) < 0.999 ? halfGap : 0);

    return {
        x: Math.max(workArea.x, fx),
        y: Math.max(workArea.y, fy),
        width: Math.max(50, fw),
        height: Math.max(50, fh)
    };
}

// Find layout for screen
function getLayoutForScreen(screen) {
    if (!screen) return state.layouts[0];
    var layoutId = state.activeLayouts[screen.name] || state.activeLayouts["default"];
    if (layoutId) {
        for (var i = 0; i < state.layouts.length; i++) {
            if (state.layouts[i].id === layoutId) {
                return state.layouts[i];
            }
        }
    }
    var geom = screen.geometry;
    var ratio = geom.width / geom.height;
    if (ratio > 3.0) {
        return state.layouts[0];
    } else if (ratio > 2.0) {
        return state.layouts[1];
    } else if (ratio < 0.8) {
        return state.layouts[7];
    }
    return state.layouts[6];
}

// Safely detach windows from tile tree to prevent automatic full-screen maximization on layout rebuild
function unmanageTileWindows(tile) {
    if (!tile) return;
    if (tile.windows) {
        var wins = tile.windows.slice();
        for (var i = 0; i < wins.length; i++) {
            try {
                tile.unmanage(wins[i]);
            } catch (e) {}
        }
    }
    if (tile.tiles) {
        for (var j = 0; j < tile.tiles.length; j++) {
            unmanageTileWindows(tile.tiles[j]);
        }
    }
}

// Synchronize KWin native TileManager tree with multi-pass constraint convergence
function syncNativeKWinTiles(layoutId) {
    var targetLayout = null;
    for (var lIdx = 0; lIdx < state.layouts.length; lIdx++) {
        if (state.layouts[lIdx].id === layoutId) {
            targetLayout = state.layouts[lIdx];
            break;
        }
    }
    if (!targetLayout) targetLayout = state.layouts[0];

    for (var sIdx = 0; sIdx < workspace.screens.length; sIdx++) {
        var screen = workspace.screens[sIdx];
        for (var dIdx = 0; dIdx < workspace.desktops.length; dIdx++) {
            var desktop = workspace.desktops[dIdx];
            try {
                var root = workspace.rootTile(screen, desktop);
                if (!root) continue;

                // 1. Unmanage windows first so KWin does not maximize them to rootTile
                unmanageTileWindows(root);

                // 2. Reset rootTile down to empty
                while (root.tiles && root.tiles.length > 0) {
                    root.tiles[0].remove();
                }

                // 3. Create required tile nodes
                if (targetLayout.id === "rows-2") {
                    root.split(2); // 2 rows
                } else if (targetLayout.id === "grid-2x2") {
                    root.split(1);
                    if (root.tiles.length >= 2) {
                        root.tiles[0].split(2);
                        root.tiles[1].split(2);
                    }
                } else if (targetLayout.id === "grid-3x2") {
                    root.split(1);
                    if (root.tiles.length >= 2) {
                        root.tiles[1].split(1);
                        if (root.tiles.length >= 3) {
                            root.tiles[0].split(2);
                            root.tiles[1].split(2);
                            root.tiles[2].split(2);
                        }
                    }
                } else if (targetLayout.id === "ultrawide-master-4") {
                    root.split(1);
                    if (root.tiles.length >= 2) {
                        root.tiles[1].split(1);
                        if (root.tiles.length >= 3) {
                            root.tiles[0].split(2);
                            root.tiles[2].split(2);
                        }
                    }
                } else {
                    while (root.tiles.length < targetLayout.zones.length) {
                        if (root.tiles.length === 0) {
                            root.split(1);
                        } else {
                            root.tiles[root.tiles.length - 1].split(1);
                        }
                    }
                }

                // 4. Multi-pass assignment to ensure KWin internal sibling constraint solver fully converges
                for (var pass = 0; pass < 2; pass++) {
                    for (var zIdx = 0; zIdx < targetLayout.zones.length && zIdx < root.tiles.length; zIdx++) {
                        var z = targetLayout.zones[zIdx];
                        root.tiles[zIdx].relativeGeometry = {
                            x: z[0],
                            y: z[1],
                            width: z[2],
                            height: z[3]
                        };
                    }
                }
            } catch (e) {
                log("Error syncing native tiles on " + screen.name + ": " + e);
            }
        }
    }
    log("Native KWin tile tree updated with exact converged proportions for layout: " + layoutId);
}

// Calculate all pixel zone rectangles for a screen
function getScreenZoneRects(screen) {
    var layout = getLayoutForScreen(screen);
    var workArea = workspace.clientArea(KWin.MaximizeArea, screen, workspace.currentDesktop);
    var gap = state.settings.gap || 8;
    var margin = state.settings.margin || 8;

    var rects = [];
    for (var i = 0; i < layout.zones.length; i++) {
        var r = computeZoneRect(layout.zones[i], workArea, gap, margin);
        r.zoneIndex = i + 1;
        rects.push(r);
    }
    return rects;
}

// Switch active layout for the current screen
function switchLayout(shortcutNum) {
    var screen = workspace.activeScreen;
    if (!screen && workspace.activeWindow) {
        screen = workspace.activeWindow.output;
    }
    if (!screen) {
        screen = workspace.screens[0];
    }
    
    var targetLayout = null;
    for (var i = 0; i < state.layouts.length; i++) {
        if (state.layouts[i].shortcut === shortcutNum) {
            targetLayout = state.layouts[i];
            break;
        }
    }
    if (!targetLayout && shortcutNum >= 1 && shortcutNum <= state.layouts.length) {
        targetLayout = state.layouts[shortcutNum - 1];
    }

    if (targetLayout && screen) {
        log("Switching layout for " + screen.name + " to: " + targetLayout.name);
        state.activeLayouts[screen.name] = targetLayout.id;
        state.activeLayouts["default"] = targetLayout.id;

        // Sync native KWin tiles silently (windows remain at their current size and position)
        syncNativeKWinTiles(targetLayout.id);

        // 1. Update shared DBus Daemon state so Plasmoid widget syncs immediately
        callDBus("org.kde.FancyZones", "/Manager", "org.kde.FancyZones", "SetLayout", screen.name, targetLayout.id, function(res) {});

        // 2. Trigger 1-second non-intrusive on-screen visual highlight of the new zones
        callDBus("org.kde.FancyZones", "/Manager", "org.kde.FancyZones", "ShowZonesOverlay", targetLayout.id, 500, function(res) {});
    }
}

// Auto-arrange all open normal windows on the active screen into the current zone layout
function autoArrangeAllWindows() {
    var screen = workspace.activeScreen || workspace.screens[0];
    var rects = getScreenZoneRects(screen);
    if (rects.length === 0) return;

    var wins = workspace.windowList();
    var normalWins = [];
    for (var i = 0; i < wins.length; i++) {
        var w = wins[i];
        if (w && w.normalWindow && !w.minimized && !w.desktopWindow && !w.dock) {
            normalWins.push(w);
        }
    }

    log("Auto-arranging " + normalWins.length + " windows into " + rects.length + " zones on " + screen.name);
    for (var j = 0; j < normalWins.length; j++) {
        var targetRect = rects[j % rects.length];
        normalWins[j].frameGeometry = {
            x: targetRect.x,
            y: targetRect.y,
            width: targetRect.width,
            height: targetRect.height
        };
    }
}

// Cycle to next / previous layout
function cycleLayout(delta) {
    var screen = workspace.activeScreen || workspace.screens[0];
    var current = getLayoutForScreen(screen);
    var currentIndex = 0;
    for (var i = 0; i < state.layouts.length; i++) {
        if (state.layouts[i].id === current.id) {
            currentIndex = i;
            break;
        }
    }
    var nextIndex = (currentIndex + delta + state.layouts.length) % state.layouts.length;
    var nextLayout = state.layouts[nextIndex];
    if (nextLayout) {
        switchLayout(nextLayout.shortcut || (nextIndex + 1));
    }
}

// Snap active window to specific zone index (1-based)
function snapActiveWindowToZone(zoneIndex) {
    var win = workspace.activeWindow;
    if (!win || !win.normalWindow) return;

    var screen = win.output || workspace.activeScreen;
    var rects = getScreenZoneRects(screen);
    if (zoneIndex >= 1 && zoneIndex <= rects.length) {
        var target = rects[zoneIndex - 1];
        log("Snapping active window " + win.caption + " to zone " + zoneIndex + " on " + screen.name);
        win.frameGeometry = {
            x: target.x,
            y: target.y,
            width: target.width,
            height: target.height
        };
    }
}

// Snap active window delta (-1 = left/prev, +1 = right/next)
function snapActiveWindowDelta(delta) {
    var win = workspace.activeWindow;
    if (!win || !win.normalWindow) return;

    var screen = win.output || workspace.activeScreen;
    var rects = getScreenZoneRects(screen);
    if (rects.length === 0) return;

    var currentGeom = win.frameGeometry;
    var curCenterX = currentGeom.x + currentGeom.width / 2;
    var curCenterY = currentGeom.y + currentGeom.height / 2;

    var closestIdx = 0;
    var minDist = 999999;
    for (var i = 0; i < rects.length; i++) {
        var r = rects[i];
        var cx = r.x + r.width / 2;
        var cy = r.y + r.height / 2;
        var d = Math.hypot(curCenterX - cx, curCenterY - cy);
        if (d < minDist) {
            minDist = d;
            closestIdx = i;
        }
    }

    var nextIdx = (closestIdx + delta + rects.length) % rects.length;
    snapActiveWindowToZone(nextIdx + 1);
}

// Snap active window directional
function snapActiveWindowDirection(dir) {
    var win = workspace.activeWindow;
    if (!win || !win.normalWindow) return;

    var screen = win.output || workspace.activeScreen;
    var rects = getScreenZoneRects(screen);
    if (rects.length <= 1) return;

    var currentGeom = win.frameGeometry;
    var curCenterX = currentGeom.x + currentGeom.width / 2;
    var curCenterY = currentGeom.y + currentGeom.height / 2;

    var bestIdx = -1;
    var bestScore = 999999;

    for (var i = 0; i < rects.length; i++) {
        var r = rects[i];
        var cx = r.x + r.width / 2;
        var cy = r.y + r.height / 2;

        if (dir === "up" && cy < curCenterY - 10) {
            var score = Math.abs(cx - curCenterX) + Math.abs(cy - curCenterY);
            if (score < bestScore) { bestScore = score; bestIdx = i; }
        } else if (dir === "down" && cy > curCenterY + 10) {
            var score = Math.abs(cx - curCenterX) + Math.abs(cy - curCenterY);
            if (score < bestScore) { bestScore = score; bestIdx = i; }
        }
    }

    if (bestIdx !== -1) {
        snapActiveWindowToZone(bestIdx + 1);
    }
}

// Launch Layout Editor
function launchEditor() {
    log("Launching FancyZones Layout Editor via DBus...");
    callDBus("org.kde.FancyZones", "/Manager", "org.kde.FancyZones", "OpenEditor", function(res) {
        log("Editor launch result: " + res);
    });
}

// Initial sync of native KWin tiles across all desktops on script startup
var initLayout = state.layouts[0];
if (initLayout) {
    syncNativeKWinTiles(initLayout.id);
}

// Register Global Keyboard Shortcuts
registerShortcut("FancyZonesLayout1", "FancyZones: Layout 1 (Priority Grid)", "Meta+Ctrl+Alt+1", function() { switchLayout(1); });
registerShortcut("FancyZonesLayout2", "FancyZones: Layout 2 (3 Columns)", "Meta+Ctrl+Alt+2", function() { switchLayout(2); });
registerShortcut("FancyZonesLayout3", "FancyZones: Layout 3 (4 Columns)", "Meta+Ctrl+Alt+3", function() { switchLayout(3); });
registerShortcut("FancyZonesLayout4", "FancyZones: Layout 4 (Dual 16:9 Split)", "Meta+Ctrl+Alt+4", function() { switchLayout(4); });
registerShortcut("FancyZonesLayout5", "FancyZones: Layout 5 (Master + 4 Flanks)", "Meta+Ctrl+Alt+5", function() { switchLayout(5); });
registerShortcut("FancyZonesLayout6", "FancyZones: Layout 6 (Grid 3x2)", "Meta+Ctrl+Alt+6", function() { switchLayout(6); });
registerShortcut("FancyZonesLayout7", "FancyZones: Layout 7 (Grid 2x2)", "Meta+Ctrl+Alt+7", function() { switchLayout(7); });
registerShortcut("FancyZonesLayout8", "FancyZones: Layout 8 (2 Rows)", "Meta+Ctrl+Alt+8", function() { switchLayout(8); });
registerShortcut("FancyZonesLayout9", "FancyZones: Layout 9 (Focus)", "Meta+Ctrl+Alt+9", function() { switchLayout(9); });

registerShortcut("FancyZonesNextLayout", "FancyZones: Next Layout", "Meta+Ctrl+Alt+Right", function() { cycleLayout(1); });
registerShortcut("FancyZonesPrevLayout", "FancyZones: Previous Layout", "Meta+Ctrl+Alt+Left", function() { cycleLayout(-1); });

registerShortcut("FancyZonesAutoArrange", "FancyZones: Auto-Arrange All Windows", "Meta+Ctrl+Alt+A", function() { autoArrangeAllWindows(); });

registerShortcut("FancyZonesSnapLeft", "FancyZones: Snap Window Left / Prev Zone", "Meta+Left", function() { snapActiveWindowDelta(-1); });
registerShortcut("FancyZonesSnapRight", "FancyZones: Snap Window Right / Next Zone", "Meta+Right", function() { snapActiveWindowDelta(1); });
registerShortcut("FancyZonesSnapUp", "FancyZones: Snap Window Up", "Meta+Up", function() { snapActiveWindowDirection("up"); });
registerShortcut("FancyZonesSnapDown", "FancyZones: Snap Window Down", "Meta+Down", function() { snapActiveWindowDirection("down"); });

registerShortcut("FancyZonesSnapZone1", "FancyZones: Snap to Zone 1", "Meta+Ctrl+1", function() { snapActiveWindowToZone(1); });
registerShortcut("FancyZonesSnapZone2", "FancyZones: Snap to Zone 2", "Meta+Ctrl+2", function() { snapActiveWindowToZone(2); });
registerShortcut("FancyZonesSnapZone3", "FancyZones: Snap to Zone 3", "Meta+Ctrl+3", function() { snapActiveWindowToZone(3); });
registerShortcut("FancyZonesSnapZone4", "FancyZones: Snap to Zone 4", "Meta+Ctrl+4", function() { snapActiveWindowToZone(4); });
registerShortcut("FancyZonesSnapZone5", "FancyZones: Snap to Zone 5", "Meta+Ctrl+5", function() { snapActiveWindowToZone(5); });
registerShortcut("FancyZonesSnapZone6", "FancyZones: Snap to Zone 6", "Meta+Ctrl+6", function() { snapActiveWindowToZone(6); });

registerShortcut("FancyZonesOpenEditor", "FancyZones: Open Layout Editor", "Meta+Shift+Z", function() { launchEditor(); });

log("FancyZones KWin Snapping Engine Initialized Successfully.");
