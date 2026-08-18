#!/usr/bin/env python3
"""
FancyZones DBus Service (org.kde.FancyZones /Manager)
Provides DBus IPC for KWin script, Plasma widget, and keyboard shortcuts.
Includes full-screen 1-second on-screen zone highlight overlay matching actual zone sizes.
"""

import sys
import os
import subprocess
import copy
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "daemon"))

from fancyzones_daemon import load_config, save_config, get_connected_screens
from default_layouts import DEFAULT_LAYOUTS

from PyQt6.QtCore import Qt, QTimer, QRectF, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QLinearGradient, QScreen
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtDBus import QDBusConnection

overlay_instances = []

class ZoneOverlayWindow(QWidget):
    """
    Full-screen, click-through, 1-second floating visual HUD
    that highlights every zone at its EXACT full-screen physical size and position.
    """
    def __init__(self, target_screen: QScreen, layout_name: str, zones: List[List[float]], gap: int = 8, margin: int = 8, duration_ms: int = 500):
        super().__init__()
        self.target_screen = target_screen
        self.layout_name = layout_name
        self.zones = zones
        self.gap = max(0, gap)
        self.margin = max(0, margin)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.BypassWindowManagerHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setScreen(target_screen)
        self.setGeometry(target_screen.geometry())

        # Automatically close after duration
        QTimer.singleShot(duration_ms, self.fade_and_close)

    def fade_and_close(self):
        global overlay_instances
        self.close()
        if self in overlay_instances:
            overlay_instances.remove(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        sw = self.width()
        sh = self.height()

        # Subtle dark backdrop tint across entire screen
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))

        # Top Center HUD Pill showing active layout name
        banner_w = min(460, int(sw * 0.4))
        banner_h = 48
        banner_rect = QRectF((sw - banner_w) / 2, 28, banner_w, banner_h)
        painter.setPen(QPen(QColor(61, 174, 233, 220), 2))
        painter.setBrush(QBrush(QColor(20, 24, 28, 235)))
        painter.drawRoundedRect(banner_rect, 12, 12)

        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Noto Sans", 13, QFont.Weight.Bold))
        painter.drawText(banner_rect, Qt.AlignmentFlag.AlignCenter, f"FancyZones: {self.layout_name}")

        # Draw each zone at its ACTUAL full-screen physical size and position!
        work_w = sw - (2 * self.margin)
        work_h = sh - (2 * self.margin)
        half_gap = self.gap / 2.0

        for idx, z in enumerate(self.zones):
            zx, zy, zw, zh = z
            
            # Real physical screen pixel bounding box
            px = self.margin + zx * work_w
            py = self.margin + zy * work_h
            pw = zw * work_w
            ph = zh * work_h

            # Inset with zone gaps
            inset_x = px + (half_gap if zx > 0.001 else 0)
            inset_y = py + (half_gap if zy > 0.001 else 0)
            inset_w = pw - (half_gap if zx > 0.001 else 0) - (half_gap if (zx + zw) < 0.999 else 0)
            inset_h = ph - (half_gap if zy > 0.001 else 0) - (half_gap if (zy + zh) < 0.999 else 0)

            rect = QRectF(inset_x, inset_y, inset_w, inset_h)

            # Zone glowing translucent body
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            grad.setColorAt(0.0, QColor(41, 140, 204, 110))
            grad.setColorAt(1.0, QColor(22, 100, 150, 140))

            painter.setPen(QPen(QColor(61, 174, 233, 235), 3))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect, 10, 10)

            # Large Zone Number Badge in center of actual zone
            badge_size = max(36.0, min(64.0, min(rect.width(), rect.height()) * 0.25))
            badge_rect = QRectF(
                rect.center().x() - badge_size / 2,
                rect.center().y() - badge_size / 2 - 16,
                badge_size,
                badge_size
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(29, 128, 184, 240)))
            painter.drawEllipse(badge_rect)

            painter.setPen(QPen(QColor("#ffffff")))
            painter.setFont(QFont("Noto Sans", max(11, int(badge_size * 0.45)), QFont.Weight.Bold))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(idx + 1))

            # Exact Pixels & Percentages on physical zone
            calc_pw = int(round(zw * sw))
            calc_ph = int(round(zh * sh))
            calc_pct_w = int(round(zw * 100))
            calc_pct_h = int(round(zh * 100))

            # Line 1: Exact Pixels
            dim_rect_px = QRectF(rect.x(), rect.center().y() + badge_size / 2 - 6, rect.width(), 24)
            painter.setFont(QFont("Noto Sans", 13, QFont.Weight.Bold))
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawText(dim_rect_px, Qt.AlignmentFlag.AlignCenter, f"{calc_pw} × {calc_ph} px")

            # Line 2: Percentage
            dim_rect_pct = QRectF(rect.x(), rect.center().y() + badge_size / 2 + 18, rect.width(), 20)
            painter.setFont(QFont("Noto Sans", 11, QFont.Weight.DemiBold))
            painter.setPen(QPen(QColor("#9ee0ff")))
            painter.drawText(dim_rect_pct, Qt.AlignmentFlag.AlignCenter, f"({calc_pct_w}% × {calc_pct_h}%)")


class FancyZonesDBusManager(QObject):
    layoutChanged = pyqtSignal(str, str)

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.config = load_config()

    @pyqtSlot(result=str)
    def OpenEditor(self):
        print("[FancyZones Service] OpenEditor invoked.")
        editor_script = ROOT_DIR / "editor" / "main.py"
        uv_bin = Path.home() / ".local/bin/uv"
        try:
            if uv_bin.exists():
                subprocess.Popen([str(uv_bin), "run", "--with", "PyQt6", "python3", str(editor_script)])
            else:
                subprocess.Popen(["python3", str(editor_script)])
            return "Editor launched"
        except Exception as e:
            return f"Error: {e}"

    @pyqtSlot(str, str, result=bool)
    def SetLayout(self, screen_name, layout_id):
        print(f"[FancyZones Service] SetLayout: screen={screen_name}, layout={layout_id}")
        self.config = load_config()
        self.config.setdefault("activeLayouts", {})[str(screen_name)] = str(layout_id)
        self.config["activeLayouts"]["default"] = str(layout_id)
        save_config(self.config)
        self.layoutChanged.emit(str(screen_name), str(layout_id))
        return True

    @pyqtSlot(str, result=str)
    def GetActiveLayout(self, screen_name):
        self.config = load_config()
        return self.config.get("activeLayouts", {}).get(str(screen_name), self.config.get("activeLayouts", {}).get("default", "cols-3"))

    @pyqtSlot(str, int, result=bool)
    def ShowZonesOverlay(self, layout_id, duration_ms):
        global overlay_instances
        print(f"[FancyZones Service] ShowZonesOverlay: {layout_id} for {duration_ms}ms")
        
        self.config = load_config()
        target_layout = None
        for l in self.config.get("layouts", DEFAULT_LAYOUTS):
            if l.get("id") == str(layout_id):
                target_layout = l
                break
        if not target_layout:
            for l in DEFAULT_LAYOUTS:
                if l.get("id") == str(layout_id):
                    target_layout = l
                    break
        if not target_layout:
            target_layout = DEFAULT_LAYOUTS[0]

        gap = self.config.get("settings", {}).get("gap", 8)
        margin = self.config.get("settings", {}).get("margin", 8)
        dur = int(duration_ms) if duration_ms > 0 else 500

        # Create full-screen overlay for all connected screens at their actual resolution
        for screen in self.app.screens():
            ov = ZoneOverlayWindow(
                screen,
                target_layout.get("name", "Layout"),
                target_layout.get("zones", []),
                gap=gap,
                margin=margin,
                duration_ms=dur
            )
            ov.showFullScreen()
            overlay_instances.append(ov)

        return True

    @pyqtSlot(int, result=bool)
    def SnapActiveWindow(self, zone_index):
        subprocess.run(["qdbus6", "org.kde.kglobalaccel", "/component/kwin", "org.kde.kglobalaccel.Component.invokeShortcut", f"FancyZonesSnapZone{zone_index}"], capture_output=True)
        return True

    @pyqtSlot(result=bool)
    def AutoArrange(self):
        subprocess.run(["qdbus6", "org.kde.kglobalaccel", "/component/kwin", "org.kde.kglobalaccel.Component.invokeShortcut", "FancyZonesAutoArrange"], capture_output=True)
        return True


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    manager = FancyZonesDBusManager(app)
    bus = QDBusConnection.sessionBus()

    if not bus.registerService("org.kde.FancyZones"):
        print("[FancyZones Service] Could not register service or already running.")
        return

    bus.registerObject("/Manager", "org.kde.FancyZones", manager, QDBusConnection.RegisterOption.ExportAllSlots | QDBusConnection.RegisterOption.ExportAllSignals)

    print("[FancyZones Service] org.kde.FancyZones /Manager with Full-Screen Overlay ready.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
