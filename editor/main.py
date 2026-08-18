#!/usr/bin/env python3
"""
FancyZones Visual Layout Editor for KDE Plasma 6
Interactive drag-and-drop zone designer, border resizing, pixel & percentage HUD,
context-aware manual dimension input modal, and fully responsive adaptive layout.
"""

import sys
import os
import copy
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add parent directory to path for daemon utils
sys.path.insert(0, str(Path(__file__).parent.parent / "daemon"))
from utils import detect_aspect_ratio, compute_zone_pixels
from default_layouts import DEFAULT_LAYOUTS, DEFAULT_SETTINGS
from fancyzones_daemon import load_config, save_config, get_connected_screens

from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QIcon, QLinearGradient, QAction, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QSpinBox, QDoubleSpinBox, QLineEdit,
    QFrame, QScrollArea, QSplitter, QDialog, QMessageBox, QGroupBox,
    QTabWidget, QGridLayout, QSizePolicy, QToolTip, QDialogButtonBox
)

class ZoneDimensionsDialog(QDialog):
    """
    Context-aware modal dialog for precise manual pixel and percentage input.
    Detects if layout is purely vertical columns, purely horizontal rows, or 2D grid,
    and displays only the relevant dimension inputs.
    """
    def __init__(self, zone_idx: int, zones: List[List[float]], screen_w: int, screen_h: int, parent=None):
        super().__init__(parent)
        self.zone_idx = zone_idx
        self.zones = copy.deepcopy(zones)
        self.screen_w = max(640, screen_w)
        self.screen_h = max(480, screen_h)
        self.target_zone = self.zones[zone_idx] # [x, y, w, h]

        # Analyze layout structure to determine context
        self.is_pure_vertical = all(abs(z[1] - 0.0) < 0.001 and abs(z[3] - 1.0) < 0.001 for z in self.zones)
        self.is_pure_horizontal = all(abs(z[0] - 0.0) < 0.001 and abs(z[2] - 1.0) < 0.001 for z in self.zones)

        self.setWindowTitle(f"Zone {zone_idx + 1} — Manual Dimensions")
        self.setFixedWidth(460)
        self.setStyleSheet("""
            QDialog { background-color: #1e2227; color: #f2f4f7; }
            QLabel { color: #e0e6ed; font-size: 12px; }
            QGroupBox { border: 1px solid #3a4047; border-radius: 8px; margin-top: 14px; padding-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #3daee9; }
            QSpinBox, QDoubleSpinBox { background-color: #252a2f; border: 1px solid #3f4750; border-radius: 6px; padding: 6px 10px; color: #ffffff; font-size: 13px; font-weight: bold; }
            QSpinBox:focus, QDoubleSpinBox:focus { border-color: #3daee9; }
            QPushButton { background-color: #2e353b; border: 1px solid #4a545e; border-radius: 6px; padding: 8px 18px; font-weight: bold; min-height: 28px; }
            QPushButton:hover { background-color: #3d474f; border-color: #3daee9; }
            QPushButton#primaryBtn { background-color: #1d80b8; border: 1px solid #3daee9; color: #ffffff; }
            QPushButton#primaryBtn:hover { background-color: #3daee9; }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header Info Banner
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #252a2f; border-radius: 8px; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)

        icon_lbl = QLabel("📐")
        icon_lbl.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        title_lbl = QLabel(f"<b>Zone {self.zone_idx + 1} of {len(self.zones)}</b>")
        title_lbl.setStyleSheet("font-size: 14px; color: #3daee9;")
        info_col.addWidget(title_lbl)

        disp_lbl = QLabel(f"Target Display: {self.screen_w} × {self.screen_h} px")
        disp_lbl.setStyleSheet("font-size: 11px; color: #9aa6b2;")
        info_col.addWidget(disp_lbl)

        header_layout.addLayout(info_col)
        header_layout.addStretch()
        layout.addWidget(header_frame)

        cur_zx, cur_zy, cur_zw, cur_zh = self.target_zone
        cur_px_w = int(round(cur_zw * self.screen_w))
        cur_px_h = int(round(cur_zh * self.screen_h))
        cur_pct_w = cur_zw * 100.0
        cur_pct_h = cur_zh * 100.0

        if self.is_pure_vertical:
            w_box = QGroupBox("Width (Vertical Split)")
            w_layout = QGridLayout(w_box)
            w_layout.setSpacing(10)

            w_layout.addWidget(QLabel("Pixels (px):"), 0, 0)
            self.width_px_spin = QSpinBox()
            self.width_px_spin.setRange(100, self.screen_w)
            self.width_px_spin.setSuffix(" px")
            self.width_px_spin.setValue(cur_px_w)
            w_layout.addWidget(self.width_px_spin, 0, 1)

            w_layout.addWidget(QLabel("Percentage (%):"), 1, 0)
            self.width_pct_spin = QDoubleSpinBox()
            self.width_pct_spin.setRange(5.0, 100.0)
            self.width_pct_spin.setDecimals(1)
            self.width_pct_spin.setSuffix(" %")
            self.width_pct_spin.setValue(cur_pct_w)
            w_layout.addWidget(self.width_pct_spin, 1, 1)

            self.width_px_spin.valueChanged.connect(self._on_w_px_changed)
            self.width_pct_spin.valueChanged.connect(self._on_w_pct_changed)
            layout.addWidget(w_box)

            note_lbl = QLabel("ℹ Height is locked to 100% (full screen height) for vertical column presets.")
            note_lbl.setStyleSheet("color: #8c96a0; font-size: 11px; font-style: italic;")
            layout.addWidget(note_lbl)

        elif self.is_pure_horizontal:
            h_box = QGroupBox("Height (Horizontal Split)")
            h_layout = QGridLayout(h_box)
            h_layout.setSpacing(10)

            h_layout.addWidget(QLabel("Pixels (px):"), 0, 0)
            self.height_px_spin = QSpinBox()
            self.height_px_spin.setRange(100, self.screen_h)
            self.height_px_spin.setSuffix(" px")
            self.height_px_spin.setValue(cur_px_h)
            h_layout.addWidget(self.height_px_spin, 0, 1)

            h_layout.addWidget(QLabel("Percentage (%):"), 1, 0)
            self.height_pct_spin = QDoubleSpinBox()
            self.height_pct_spin.setRange(5.0, 100.0)
            self.height_pct_spin.setDecimals(1)
            self.height_pct_spin.setSuffix(" %")
            self.height_pct_spin.setValue(cur_pct_h)
            h_layout.addWidget(self.height_pct_spin, 1, 1)

            self.height_px_spin.valueChanged.connect(self._on_h_px_changed)
            self.height_pct_spin.valueChanged.connect(self._on_h_pct_changed)
            layout.addWidget(h_box)

            note_lbl = QLabel("ℹ Width is locked to 100% (full screen width) for horizontal row presets.")
            note_lbl.setStyleSheet("color: #8c96a0; font-size: 11px; font-style: italic;")
            layout.addWidget(note_lbl)

        else:
            dim_box = QGroupBox("Zone Dimensions (Width & Height)")
            dim_layout = QGridLayout(dim_box)
            dim_layout.setSpacing(10)

            dim_layout.addWidget(QLabel("Width (px):"), 0, 0)
            self.width_px_spin = QSpinBox()
            self.width_px_spin.setRange(100, self.screen_w)
            self.width_px_spin.setSuffix(" px")
            self.width_px_spin.setValue(cur_px_w)
            dim_layout.addWidget(self.width_px_spin, 0, 1)

            dim_layout.addWidget(QLabel("Width (%):"), 0, 2)
            self.width_pct_spin = QDoubleSpinBox()
            self.width_pct_spin.setRange(5.0, 100.0)
            self.width_pct_spin.setDecimals(1)
            self.width_pct_spin.setSuffix(" %")
            self.width_pct_spin.setValue(cur_pct_w)
            dim_layout.addWidget(self.width_pct_spin, 0, 3)

            dim_layout.addWidget(QLabel("Height (px):"), 1, 0)
            self.height_px_spin = QSpinBox()
            self.height_px_spin.setRange(100, self.screen_h)
            self.height_px_spin.setSuffix(" px")
            self.height_px_spin.setValue(cur_px_h)
            dim_layout.addWidget(self.height_px_spin, 1, 1)

            dim_layout.addWidget(QLabel("Height (%):"), 1, 2)
            self.height_pct_spin = QDoubleSpinBox()
            self.height_pct_spin.setRange(5.0, 100.0)
            self.height_pct_spin.setDecimals(1)
            self.height_pct_spin.setSuffix(" %")
            self.height_pct_spin.setValue(cur_pct_h)
            dim_layout.addWidget(self.height_pct_spin, 1, 3)

            self.width_px_spin.valueChanged.connect(self._on_w_px_changed)
            self.width_pct_spin.valueChanged.connect(self._on_w_pct_changed)
            self.height_px_spin.valueChanged.connect(self._on_h_px_changed)
            self.height_pct_spin.valueChanged.connect(self._on_h_pct_changed)

            layout.addWidget(dim_box)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply Dimensions")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.clicked.connect(self.apply_changes)
        btn_box.addWidget(apply_btn)

        layout.addLayout(btn_box)

    def _on_w_px_changed(self, px_val):
        pct = (px_val / self.screen_w) * 100.0
        self.width_pct_spin.blockSignals(True)
        self.width_pct_spin.setValue(pct)
        self.width_pct_spin.blockSignals(False)

    def _on_w_pct_changed(self, pct_val):
        px = int(round((pct_val / 100.0) * self.screen_w))
        self.width_px_spin.blockSignals(True)
        self.width_px_spin.setValue(px)
        self.width_px_spin.blockSignals(False)

    def _on_h_px_changed(self, px_val):
        pct = (px_val / self.screen_h) * 100.0
        self.height_pct_spin.blockSignals(True)
        self.height_pct_spin.setValue(pct)
        self.height_pct_spin.blockSignals(False)

    def _on_h_pct_changed(self, pct_val):
        px = int(round((pct_val / 100.0) * self.screen_h))
        self.height_px_spin.blockSignals(True)
        self.height_px_spin.setValue(px)
        self.height_px_spin.blockSignals(False)

    def apply_changes(self):
        new_w_norm = (self.width_pct_spin.value() / 100.0) if hasattr(self, "width_pct_spin") else self.target_zone[2]
        new_h_norm = (self.height_pct_spin.value() / 100.0) if hasattr(self, "height_pct_spin") else self.target_zone[3]

        if self.is_pure_vertical and len(self.zones) > 1:
            old_w = self.target_zone[2]
            delta_w = new_w_norm - old_w
            self.zones[self.zone_idx][2] = new_w_norm

            other_indices = [i for i in range(len(self.zones)) if i != self.zone_idx]
            total_other_w = sum(self.zones[i][2] for i in other_indices)
            if total_other_w > 0:
                for oi in other_indices:
                    ratio = self.zones[oi][2] / total_other_w
                    self.zones[oi][2] = max(0.05, self.zones[oi][2] - delta_w * ratio)

            cur_x = 0.0
            for k in range(len(self.zones)):
                self.zones[k][0] = cur_x
                cur_x += self.zones[k][2]

        elif self.is_pure_horizontal and len(self.zones) > 1:
            old_h = self.target_zone[3]
            delta_h = new_h_norm - old_h
            self.zones[self.zone_idx][3] = new_h_norm

            other_indices = [i for i in range(len(self.zones)) if i != self.zone_idx]
            total_other_h = sum(self.zones[i][3] for i in other_indices)
            if total_other_h > 0:
                for oi in other_indices:
                    ratio = self.zones[oi][3] / total_other_h
                    self.zones[oi][3] = max(0.05, self.zones[oi][3] - delta_h * ratio)

            cur_y = 0.0
            for k in range(len(self.zones)):
                self.zones[k][1] = cur_y
                cur_y += self.zones[k][3]

        else:
            self.zones[self.zone_idx][2] = new_w_norm
            self.zones[self.zone_idx][3] = new_h_norm

        self.accept()

    def get_updated_zones(self) -> List[List[float]]:
        return self.zones


class ZoneCanvas(QWidget):
    """
    Interactive canvas displaying the screen and zones with accurate aspect ratio.
    Allows clicking zones to select, split vertical/horizontal, merge, adjust gaps,
    drag-to-resize borders, and double-click to open the manual dimensions modal.
    """
    zoneSelected = pyqtSignal(int)
    layoutChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

        self.zones: List[List[float]] = [] # [[x, y, w, h], ...]
        self.aspect_ratio: float = 32 / 9 # width / height
        self.screen_width: int = 5120
        self.screen_height: int = 1440
        self.gap: int = 8
        self.margin: int = 8
        self.selected_zone_index: int = 0
        self.hovered_zone_index: int = -1

        # Border Drag & Resize State
        self.drag_active: bool = False
        self.drag_start_pos: QPointF = QPointF(0, 0)
        self.drag_target_zone: int = -1
        self.drag_handle: str = ""
        self.drag_initial_zones: List[List[float]] = []
        self.hover_handle: str = ""
        self.hover_zone_idx: int = -1

    def set_layout_data(self, zones: List[List[float]], aspect_ratio: float, screen_w: int, screen_h: int, gap: int, margin: int):
        self.zones = copy.deepcopy(zones)
        self.aspect_ratio = max(0.4, min(4.0, aspect_ratio))
        self.screen_width = max(640, screen_w)
        self.screen_height = max(480, screen_h)
        self.gap = gap
        self.margin = margin
        self.selected_zone_index = 0 if self.zones else -1
        self.update()

    def get_screen_bounds(self) -> QRectF:
        """Computes scaled viewport bounding box cleanly without clipping."""
        padding = max(14, min(24, int(self.width() * 0.02)))
        avail_w = max(50.0, self.width() - 2 * padding)
        avail_h = max(50.0, self.height() - 2 * padding)

        avail_ratio = avail_w / avail_h

        if avail_ratio > self.aspect_ratio:
            sh = avail_h
            sw = sh * self.aspect_ratio
        else:
            sw = avail_w
            sh = sw / self.aspect_ratio

        sx = padding + (avail_w - sw) / 2
        sy = padding + (avail_h - sh) / 2
        return QRectF(sx, sy, sw, sh)

    def find_border_handle_at_pos(self, pos: QPointF) -> Tuple[int, str]:
        bounds = self.get_screen_bounds()
        if not bounds.contains(pos):
            return -1, ""

        scale_x = bounds.width()
        scale_y = bounds.height()
        handle_thresh = 10.0

        for idx, z in enumerate(self.zones):
            zx, zy, zw, zh = z
            px = bounds.x() + zx * scale_x
            py = bounds.y() + zy * scale_y
            pw = zw * scale_x
            ph = zh * scale_y

            if abs(pos.x() - (px + pw)) <= handle_thresh and (py - 4) <= pos.y() <= (py + ph + 4):
                return idx, "right"
            if abs(pos.x() - px) <= handle_thresh and (py - 4) <= pos.y() <= (py + ph + 4):
                return idx, "left"
            if abs(pos.y() - (py + ph)) <= handle_thresh and (px - 4) <= pos.x() <= (px + pw + 4):
                return idx, "bottom"
            if abs(pos.y() - py) <= handle_thresh and (px - 4) <= pos.x() <= (px + pw + 4):
                return idx, "top"

        for idx, z in enumerate(self.zones):
            zx, zy, zw, zh = z
            px = bounds.x() + zx * scale_x
            py = bounds.y() + zy * scale_y
            pw = zw * scale_x
            ph = zh * scale_y
            if QRectF(px, py, pw, ph).contains(pos):
                return idx, "inside"

        return -1, ""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Canvas Background
        painter.fillRect(self.rect(), QColor("#191c20"))

        bounds = self.get_screen_bounds()

        # Monitor Outer Bezel
        bezel_rect = bounds.adjusted(-6, -6, 6, 6)
        painter.setPen(QPen(QColor("#384049"), 2))
        painter.setBrush(QBrush(QColor("#111417")))
        painter.drawRoundedRect(bezel_rect, 8, 8)

        # Screen Display Surface
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#20252b")))
        painter.drawRoundedRect(bounds, 4, 4)

        if not self.zones:
            painter.setPen(QPen(QColor("#808c96")))
            painter.setFont(QFont("Noto Sans", 11))
            painter.drawText(bounds, Qt.AlignmentFlag.AlignCenter, "No zones in this layout.\nClick '+ Add Zone' or choose a template.")
            return

        scale_x = bounds.width()
        scale_y = bounds.height()
        
        for idx, z in enumerate(self.zones):
            zx, zy, zw, zh = z
            px = bounds.x() + zx * scale_x
            py = bounds.y() + zy * scale_y
            pw = zw * scale_x
            ph = zh * scale_y

            inset = max(2, int(self.gap * 0.35))
            zone_rect = QRectF(px + inset, py + inset, pw - 2 * inset, ph - 2 * inset)

            is_selected = (idx == self.selected_zone_index)
            is_hovered = (idx == self.hovered_zone_index) or (idx == self.hover_zone_idx)

            grad = QLinearGradient(zone_rect.topLeft(), zone_rect.bottomRight())
            if is_selected:
                grad.setColorAt(0.0, QColor(41, 140, 204, 150))
                grad.setColorAt(1.0, QColor(22, 100, 150, 180))
                border_color = QColor("#56b6f0")
                border_width = 2.5
            elif is_hovered:
                grad.setColorAt(0.0, QColor(68, 80, 92, 160))
                grad.setColorAt(1.0, QColor(45, 54, 62, 180))
                border_color = QColor("#3daee9")
                border_width = 1.8
            else:
                grad.setColorAt(0.0, QColor(40, 47, 54, 130))
                grad.setColorAt(1.0, QColor(30, 35, 41, 160))
                border_color = QColor("#4b545d")
                border_width = 1.0

            painter.setPen(QPen(border_color, border_width))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(zone_rect, 6, 6)

            # Zone Number Badge
            badge_size = max(18.0, min(34.0, min(zone_rect.width(), zone_rect.height()) * 0.32))
            badge_rect = QRectF(
                zone_rect.center().x() - badge_size / 2,
                zone_rect.center().y() - badge_size / 2 - 12,
                badge_size,
                badge_size
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 120) if not is_selected else QColor(29, 128, 184, 230)))
            painter.drawEllipse(badge_rect)

            painter.setPen(QPen(QColor("#ffffff")))
            f = QFont("Noto Sans", max(8, int(badge_size * 0.45)), QFont.Weight.Bold)
            painter.setFont(f)
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(idx + 1))

            # Calculated Real Screen Pixels & Percentages
            pixel_w = int(round(zw * self.screen_width))
            pixel_h = int(round(zh * self.screen_height))
            pct_w = int(round(zw * 100))
            pct_h = int(round(zh * 100))

            if zone_rect.height() > 45:
                px_text = f"{pixel_w} × {pixel_h} px"
                px_rect = QRectF(zone_rect.x(), zone_rect.center().y() + badge_size / 2 - 6, zone_rect.width(), 16)
                painter.setPen(QPen(QColor("#ffffff") if is_selected else QColor("#e0e6ed")))
                painter.setFont(QFont("Noto Sans", max(7, min(9, int(zone_rect.width() * 0.05))), QFont.Weight.DemiBold))
                painter.drawText(px_rect, Qt.AlignmentFlag.AlignCenter, px_text)

                pct_text = f"({pct_w}% × {pct_h}%)"
                pct_rect = QRectF(zone_rect.x(), zone_rect.center().y() + badge_size / 2 + 10, zone_rect.width(), 14)
                painter.setPen(QPen(QColor("#8fd1f7") if is_selected else QColor("#9aa6b2")))
                painter.setFont(QFont("Noto Sans", max(7, min(8, int(zone_rect.width() * 0.045)))))
                painter.drawText(pct_rect, Qt.AlignmentFlag.AlignCenter, pct_text)

        # Active Border Drag Highlight
        if (self.hover_handle and self.hover_handle != "inside" and self.hover_zone_idx >= 0) or self.drag_active:
            target_idx = self.drag_target_zone if self.drag_active else self.hover_zone_idx
            handle = self.drag_handle if self.drag_active else self.hover_handle
            
            if 0 <= target_idx < len(self.zones):
                zx, zy, zw, zh = self.zones[target_idx]
                px = bounds.x() + zx * scale_x
                py = bounds.y() + zy * scale_y
                pw = zw * scale_x
                ph = zh * scale_y

                painter.setPen(QPen(QColor("#00ff88") if self.drag_active else QColor("#3daee9"), 4))
                if handle in ["left"]:
                    painter.drawLine(QPointF(px, py), QPointF(px, py + ph))
                elif handle in ["right"]:
                    painter.drawLine(QPointF(px + pw, py), QPointF(px + pw, py + ph))
                elif handle in ["top"]:
                    painter.drawLine(QPointF(px, py), QPointF(px + pw, py))
                elif handle in ["bottom"]:
                    painter.drawLine(QPointF(px, py + ph), QPointF(px + pw, py + ph))

    def mouseMoveEvent(self, event):
        pos = event.position()
        bounds = self.get_screen_bounds()
        scale_x = bounds.width()
        scale_y = bounds.height()

        if self.drag_active and self.drag_target_zone >= 0:
            delta_px_x = pos.x() - self.drag_start_pos.x()
            delta_px_y = pos.y() - self.drag_start_pos.y()
            delta_norm_x = delta_px_x / scale_x if scale_x > 0 else 0
            delta_norm_y = delta_px_y / scale_y if scale_y > 0 else 0

            self.zones = copy.deepcopy(self.drag_initial_zones)
            z = self.zones[self.drag_target_zone]
            orig_zx, orig_zy, orig_zw, orig_zh = z
            min_norm = 0.05

            if self.drag_handle == "right":
                new_w = max(min_norm, min(1.0 - orig_zx, orig_zw + delta_norm_x))
                self.zones[self.drag_target_zone][2] = new_w
                for j, other in enumerate(self.zones):
                    if j != self.drag_target_zone:
                        if abs(other[0] - (orig_zx + orig_zw)) < 0.01:
                            shift = new_w - orig_zw
                            other[0] = orig_zx + new_w
                            other[2] = max(min_norm, other[2] - shift)
            
            elif self.drag_handle == "left":
                new_x = max(0.0, min(orig_zx + orig_zw - min_norm, orig_zx + delta_norm_x))
                new_w = orig_zw - (new_x - orig_zx)
                self.zones[self.drag_target_zone][0] = new_x
                self.zones[self.drag_target_zone][2] = new_w
                for j, other in enumerate(self.zones):
                    if j != self.drag_target_zone:
                        if abs((other[0] + other[2]) - orig_zx) < 0.01:
                            other[2] = max(min_norm, new_x - other[0])

            elif self.drag_handle == "bottom":
                new_h = max(min_norm, min(1.0 - orig_zy, orig_zh + delta_norm_y))
                self.zones[self.drag_target_zone][3] = new_h
                for j, other in enumerate(self.zones):
                    if j != self.drag_target_zone:
                        if abs(other[1] - (orig_zy + orig_zh)) < 0.01:
                            shift = new_h - orig_zh
                            other[1] = orig_zy + new_h
                            other[3] = max(min_norm, other[3] - shift)

            elif self.drag_handle == "top":
                new_y = max(0.0, min(orig_zy + orig_zh - min_norm, orig_zy + delta_norm_y))
                new_h = orig_zh - (new_y - orig_zy)
                self.zones[self.drag_target_zone][1] = new_y
                self.zones[self.drag_target_zone][3] = new_h
                for j, other in enumerate(self.zones):
                    if j != self.drag_target_zone:
                        if abs((other[1] + other[3]) - orig_zy) < 0.01:
                            other[3] = max(min_norm, new_y - other[1])

            self.layoutChanged.emit()
            self.update()
            return

        zone_idx, handle = self.find_border_handle_at_pos(pos)
        self.hover_zone_idx = zone_idx
        self.hover_handle = handle
        self.hovered_zone_index = zone_idx if handle == "inside" else -1

        if handle in ["left", "right"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        elif handle in ["top", "bottom"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        elif handle == "inside":
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            zone_idx, handle = self.find_border_handle_at_pos(pos)

            if zone_idx >= 0 and handle in ["left", "right", "top", "bottom"]:
                self.drag_active = True
                self.drag_start_pos = pos
                self.drag_target_zone = zone_idx
                self.drag_handle = handle
                self.drag_initial_zones = copy.deepcopy(self.zones)
                self.selected_zone_index = zone_idx
                self.zoneSelected.emit(self.selected_zone_index)
            elif zone_idx >= 0:
                self.selected_zone_index = zone_idx
                self.zoneSelected.emit(self.selected_zone_index)
                self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            zone_idx, handle = self.find_border_handle_at_pos(pos)
            if zone_idx >= 0:
                self.selected_zone_index = zone_idx
                self.zoneSelected.emit(self.selected_zone_index)
                self.open_dimensions_dialog(zone_idx)

    def open_dimensions_dialog(self, zone_idx: int):
        if 0 <= zone_idx < len(self.zones):
            dlg = ZoneDimensionsDialog(zone_idx, self.zones, self.screen_width, self.screen_height, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.zones = dlg.get_updated_zones()
                self.layoutChanged.emit()
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_active:
            self.drag_active = False
            self.drag_target_zone = -1
            self.drag_handle = ""
            self.layoutChanged.emit()
            self.update()

    def split_selected_vertical(self):
        if 0 <= self.selected_zone_index < len(self.zones):
            z = self.zones[self.selected_zone_index]
            zx, zy, zw, zh = z
            half_w = zw / 2
            self.zones[self.selected_zone_index] = [zx, zy, half_w, zh]
            self.zones.insert(self.selected_zone_index + 1, [zx + half_w, zy, half_w, zh])
            self.layoutChanged.emit()
            self.update()

    def split_selected_horizontal(self):
        if 0 <= self.selected_zone_index < len(self.zones):
            z = self.zones[self.selected_zone_index]
            zx, zy, zw, zh = z
            half_h = zh / 2
            self.zones[self.selected_zone_index] = [zx, zy, zw, half_h]
            self.zones.insert(self.selected_zone_index + 1, [zx, zy + half_h, zw, half_h])
            self.layoutChanged.emit()
            self.update()

    def delete_selected_zone(self):
        if len(self.zones) > 1 and 0 <= self.selected_zone_index < len(self.zones):
            self.zones.pop(self.selected_zone_index)
            self.selected_zone_index = max(0, self.selected_zone_index - 1)
            self.layoutChanged.emit()
            self.update()


class FancyZonesEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FancyZones Layout Editor - KDE Plasma 6")
        self.setMinimumSize(1020, 640)
        self.resize(1140, 720)

        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #1b1e20; color: #f2f4f7; }
            QWidget { font-family: 'Noto Sans', 'Segoe UI', sans-serif; color: #f2f4f7; }
            QGroupBox { border: 1px solid #3a4047; border-radius: 8px; margin-top: 14px; padding-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #3daee9; }
            QPushButton { background-color: #2e353b; border: 1px solid #4a545e; border-radius: 6px; padding: 6px 12px; font-weight: 500; min-height: 28px; }
            QPushButton:hover { background-color: #3d474f; border-color: #3daee9; }
            QPushButton:pressed { background-color: #1d80b8; }
            QPushButton#primaryBtn { background-color: #1d80b8; border: 1px solid #3daee9; font-weight: bold; }
            QPushButton#primaryBtn:hover { background-color: #3daee9; color: #ffffff; }
            QComboBox, QSpinBox, QLineEdit { background-color: #252a2f; border: 1px solid #3f4750; border-radius: 6px; padding: 5px 8px; color: #ffffff; min-height: 24px; }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus { border-color: #3daee9; }
            QSlider::groove:horizontal { border: 1px solid #3a4047; height: 6px; background: #252a2f; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #3daee9; border-radius: 3px; }
            QSlider::handle:horizontal { background: #ffffff; border: 1px solid #3daee9; width: 16px; margin: -5px 0; border-radius: 8px; }
            QScrollArea { border: none; background-color: transparent; }
        """)

        self.config = load_config()
        self.screens = get_connected_screens()
        self.current_screen = self.screens[0] if self.screens else {"name": "DP-3", "geometry": {"width": 5120, "height": 1440}}
        self.current_layout_idx = 0

        self.setup_ui()
        self.load_initial_screen_and_layout()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Header Bar: Screen Selector & Aspect Ratio Badge
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #252a2f; border-radius: 8px; padding: 6px 12px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(6, 4, 6, 4)

        screen_lbl = QLabel("Display / Monitor:")
        screen_lbl.setStyleSheet("font-weight: bold; color: #c5cbd1;")
        header_layout.addWidget(screen_lbl)

        self.screen_combo = QComboBox()
        for s in self.screens:
            g = s.get("geometry", {})
            r_badge = s.get("aspectRatio", {}).get("badge", "16:9")
            self.screen_combo.addItem(f"{s.get('name', 'Display')} — {g.get('width', 1920)}×{g.get('height', 1080)} ({r_badge})", s)
        self.screen_combo.currentIndexChanged.connect(self.on_screen_changed)
        header_layout.addWidget(self.screen_combo, 2)

        self.aspect_badge_lbl = QLabel("32:9 Super Ultrawide")
        self.aspect_badge_lbl.setStyleSheet("background-color: #1d80b8; color: #ffffff; font-weight: bold; border-radius: 12px; padding: 4px 12px;")
        header_layout.addWidget(self.aspect_badge_lbl)

        header_layout.addStretch()

        open_widget_btn = QPushButton("Install to Top Bar")
        open_widget_btn.clicked.connect(self.install_to_top_bar)
        header_layout.addWidget(open_widget_btn)

        main_layout.addWidget(header_frame)

        # Middle Content Area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Left Column: Scrollable Sidebar for Presets & Templates
        left_scroll = QScrollArea()
        left_scroll.setFixedWidth(230)
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(8)

        left_title = QLabel("Layout Presets")
        left_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #3daee9;")
        left_layout.addWidget(left_title)

        self.layout_combo = QComboBox()
        self.refresh_layout_combo()
        self.layout_combo.currentIndexChanged.connect(self.on_layout_changed)
        left_layout.addWidget(self.layout_combo)

        # Properties Box
        details_box = QGroupBox("Properties")
        details_layout = QVBoxLayout(details_box)
        details_layout.setSpacing(6)

        details_layout.addWidget(QLabel("Layout Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_name_edited)
        details_layout.addWidget(self.name_edit)

        details_layout.addWidget(QLabel("Hotkey Index (1-9):"))
        self.shortcut_spin = QSpinBox()
        self.shortcut_spin.setRange(1, 9)
        self.shortcut_spin.valueChanged.connect(self.on_shortcut_changed)
        details_layout.addWidget(self.shortcut_spin)

        left_layout.addWidget(details_box)

        # Templates Box (2-column compact grid to prevent vertical squishing!)
        template_box = QGroupBox("Templates")
        template_grid = QGridLayout(template_box)
        template_grid.setContentsMargins(6, 12, 6, 6)
        template_grid.setSpacing(6)

        templates_list = [
            ("Priority Grid", "priority-grid"),
            ("3 Columns", "cols-3"),
            ("4 Columns", "cols-4"),
            ("Dual 16:9", "dual-split"),
            ("Master+4", "ultrawide-master-4"),
            ("Grid 3x2", "grid-3x2"),
            ("Grid 2x2", "grid-2x2"),
            ("2 Rows", "rows-2"),
            ("Focus", "focus")
        ]

        for i, (t_name, t_id) in enumerate(templates_list):
            btn = QPushButton(t_name)
            btn.setStyleSheet("padding: 4px 6px; font-size: 11px; min-height: 26px;")
            btn.clicked.connect(lambda _, tid=t_id: self.apply_template_by_id(tid))
            template_grid.addWidget(btn, i // 2, i % 2)

        left_layout.addWidget(template_box)

        new_layout_btn = QPushButton("+ New Custom Layout")
        new_layout_btn.setStyleSheet("min-height: 28px;")
        new_layout_btn.clicked.connect(self.create_new_layout)
        left_layout.addWidget(new_layout_btn)

        left_layout.addStretch()
        left_scroll.setWidget(left_widget)
        content_layout.addWidget(left_scroll)

        # Center Column: Zone Canvas Viewport + Responsive Bottom Bar
        center_panel = QFrame()
        center_panel.setStyleSheet("background-color: #1e2227; border-radius: 8px;")
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(8, 8, 8, 8)
        center_layout.setSpacing(6)

        self.canvas = ZoneCanvas()
        self.canvas.zoneSelected.connect(self.on_zone_selected)
        self.canvas.layoutChanged.connect(self.on_canvas_layout_changed)
        center_layout.addWidget(self.canvas, 1)

        # Status Line
        self.selected_zone_lbl = QLabel("Selected: Zone 1")
        self.selected_zone_lbl.setStyleSheet("color: #3daee9; font-weight: bold; font-size: 12px; padding: 2px 4px;")
        center_layout.addWidget(self.selected_zone_lbl)

        # Responsive Canvas Toolbar
        canvas_tools = QHBoxLayout()
        canvas_tools.setSpacing(6)

        split_v_btn = QPushButton("✂ Split Vertical")
        split_v_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        split_v_btn.clicked.connect(self.canvas.split_selected_vertical)
        canvas_tools.addWidget(split_v_btn)

        split_h_btn = QPushButton("✂ Split Horizontal")
        split_h_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        split_h_btn.clicked.connect(self.canvas.split_selected_horizontal)
        canvas_tools.addWidget(split_h_btn)

        edit_dim_btn = QPushButton("📐 Sizing (px/%)")
        edit_dim_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        edit_dim_btn.clicked.connect(lambda: self.canvas.open_dimensions_dialog(self.canvas.selected_zone_index))
        canvas_tools.addWidget(edit_dim_btn)

        del_zone_btn = QPushButton("🗑 Delete")
        del_zone_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        del_zone_btn.clicked.connect(self.canvas.delete_selected_zone)
        canvas_tools.addWidget(del_zone_btn)

        add_free_btn = QPushButton("+ Add Zone")
        add_free_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        add_free_btn.clicked.connect(self.add_free_zone)
        canvas_tools.addWidget(add_free_btn)

        center_layout.addLayout(canvas_tools)
        content_layout.addWidget(center_panel, 1)

        # Right Column: Scrollable Settings & Shortcuts
        right_scroll = QScrollArea()
        right_scroll.setFixedWidth(230)
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(8)

        right_title = QLabel("Spacing & Gaps")
        right_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #3daee9;")
        right_layout.addWidget(right_title)

        # Gap Slider
        gap_lbl_row = QHBoxLayout()
        gap_lbl_row.addWidget(QLabel("Zone Gap:"))
        self.gap_val_lbl = QLabel(f"{self.config.get('settings', {}).get('gap', 8)}px")
        self.gap_val_lbl.setStyleSheet("font-weight: bold; color: #3daee9;")
        gap_lbl_row.addWidget(self.gap_val_lbl)
        right_layout.addLayout(gap_lbl_row)

        self.gap_slider = QSlider(Qt.Orientation.Horizontal)
        self.gap_slider.setRange(0, 32)
        self.gap_slider.setValue(self.config.get("settings", {}).get("gap", 8))
        self.gap_slider.valueChanged.connect(self.on_gap_changed)
        right_layout.addWidget(self.gap_slider)

        # Margin Slider
        margin_lbl_row = QHBoxLayout()
        margin_lbl_row.addWidget(QLabel("Screen Margin:"))
        self.margin_val_lbl = QLabel(f"{self.config.get('settings', {}).get('margin', 8)}px")
        self.margin_val_lbl.setStyleSheet("font-weight: bold; color: #3daee9;")
        margin_lbl_row.addWidget(self.margin_val_lbl)
        right_layout.addLayout(margin_lbl_row)

        self.margin_slider = QSlider(Qt.Orientation.Horizontal)
        self.margin_slider.setRange(0, 32)
        self.margin_slider.setValue(self.config.get("settings", {}).get("margin", 8))
        self.margin_slider.valueChanged.connect(self.on_margin_changed)
        right_layout.addWidget(self.margin_slider)

        # Help Note
        help_box = QGroupBox("Zone Sizing")
        help_layout = QVBoxLayout(help_box)
        help_layout.setSpacing(4)
        help_lbl = QLabel(
            "• <b>Double-Click</b> any zone for exact px & % input.<br>"
            "• <b>Drag Borders</b> to resize.<br>"
            "• Pure vertical columns lock to width."
        )
        help_lbl.setTextFormat(Qt.TextFormat.RichText)
        help_lbl.setStyleSheet("font-size: 11px; color: #9aa6b2; line-height: 130%;")
        help_lbl.setWordWrap(True)
        help_layout.addWidget(help_lbl)
        right_layout.addWidget(help_box)

        # Shortcuts Box
        shortcuts_box = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_box)
        shortcuts_layout.setSpacing(4)

        info_text = (
            "<b>Shift + Drag</b>: Snap window<br>"
            "<b>Meta+Ctrl+Alt+[1-9]</b>: Switch<br>"
            "<b>Meta+Ctrl+Alt+A</b>: Auto-Arrange<br>"
            "<b>Meta+←/→/↑/↓</b>: Cycle Zone<br>"
            "<b>Meta+Ctrl+[1-9]</b>: Snap #<br>"
            "<b>Meta+Shift+Z</b>: Open Editor"
        )
        shortcuts_lbl = QLabel(info_text)
        shortcuts_lbl.setTextFormat(Qt.TextFormat.RichText)
        shortcuts_lbl.setStyleSheet("font-size: 10px; color: #c5cbd1; line-height: 130%;")
        shortcuts_layout.addWidget(shortcuts_lbl)

        right_layout.addWidget(shortcuts_box)
        right_layout.addStretch()

        right_scroll.setWidget(right_widget)
        content_layout.addWidget(right_scroll)

        main_layout.addLayout(content_layout, 1)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(4, 2, 4, 2)

        status_lbl = QLabel("Changes apply instantly to KWin window manager and Plasma widget.")
        status_lbl.setStyleSheet("color: #8c96a0; font-size: 11px;")
        bottom_bar.addWidget(status_lbl)

        bottom_bar.addStretch()

        apply_screen_btn = QPushButton("Apply to This Screen")
        apply_screen_btn.clicked.connect(self.apply_to_current_screen)
        bottom_bar.addWidget(apply_screen_btn)

        save_btn = QPushButton("Save & Apply All")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save_and_apply)
        bottom_bar.addWidget(save_btn)

        main_layout.addLayout(bottom_bar)

    def refresh_layout_combo(self):
        self.layout_combo.blockSignals(True)
        self.layout_combo.clear()
        for idx, l in enumerate(self.config.get("layouts", [])):
            shortcut_tag = f" [#{l.get('shortcut', idx+1)}]" if l.get("shortcut") else ""
            self.layout_combo.addItem(f"{l.get('name', 'Layout')}{shortcut_tag}", idx)
        self.layout_combo.blockSignals(False)

    def load_initial_screen_and_layout(self):
        self.on_screen_changed(0)

    def on_screen_changed(self, idx):
        if idx < 0 or idx >= len(self.screens):
            return
        self.current_screen = self.screens[idx]
        g = self.current_screen.get("geometry", {})
        w = g.get("width", 5120)
        h = g.get("height", 1440)
        ratio_info = self.current_screen.get("aspectRatio", detect_aspect_ratio(w, h))

        self.aspect_badge_lbl.setText(ratio_info.get("badge", f"{w}:{h}"))
        
        screen_name = self.current_screen.get("name", "DP-3")
        active_id = self.config.get("activeLayouts", {}).get(screen_name, self.config.get("activeLayouts", {}).get("default", "priority-grid"))
        
        found_idx = 0
        for i, l in enumerate(self.config.get("layouts", [])):
            if l.get("id") == active_id:
                found_idx = i
                break
        
        self.layout_combo.setCurrentIndex(found_idx)
        self.load_layout_to_canvas(found_idx)

    def on_layout_changed(self, idx):
        if idx < 0:
            return
        self.load_layout_to_canvas(idx)

    def load_layout_to_canvas(self, idx):
        layouts = self.config.get("layouts", [])
        if idx < 0 or idx >= len(layouts):
            return
        self.current_layout_idx = idx
        layout_data = layouts[idx]

        self.name_edit.blockSignals(True)
        self.name_edit.setText(layout_data.get("name", ""))
        self.name_edit.blockSignals(False)

        self.shortcut_spin.blockSignals(True)
        self.shortcut_spin.setValue(layout_data.get("shortcut", idx + 1))
        self.shortcut_spin.blockSignals(False)

        g = self.current_screen.get("geometry", {})
        w = g.get("width", 5120)
        h = g.get("height", 1440)
        aspect = w / h if h > 0 else 16/9

        gap = self.config.get("settings", {}).get("gap", 8)
        margin = self.config.get("settings", {}).get("margin", 8)

        self.canvas.set_layout_data(layout_data.get("zones", []), aspect, w, h, gap, margin)
        self.on_zone_selected(0)

    def on_zone_selected(self, zone_idx):
        total = len(self.canvas.zones)
        if 0 <= zone_idx < total:
            z = self.canvas.zones[zone_idx]
            px_w = int(round(z[2] * self.canvas.screen_width))
            px_h = int(round(z[3] * self.canvas.screen_height))
            pct_w = int(round(z[2] * 100))
            pct_h = int(round(z[3] * 100))
            self.selected_zone_lbl.setText(f"Selected: Zone {zone_idx + 1} of {total} — {px_w} × {px_h} px ({pct_w}% × {pct_h}%)")
        else:
            self.selected_zone_lbl.setText("No Zone Selected")

    def on_canvas_layout_changed(self):
        layouts = self.config.get("layouts", [])
        if 0 <= self.current_layout_idx < len(layouts):
            layouts[self.current_layout_idx]["zones"] = copy.deepcopy(self.canvas.zones)
        self.on_zone_selected(self.canvas.selected_zone_index)

    def on_name_edited(self, text):
        layouts = self.config.get("layouts", [])
        if 0 <= self.current_layout_idx < len(layouts):
            layouts[self.current_layout_idx]["name"] = text
            self.refresh_layout_combo()
            self.layout_combo.setCurrentIndex(self.current_layout_idx)

    def on_shortcut_changed(self, val):
        layouts = self.config.get("layouts", [])
        if 0 <= self.current_layout_idx < len(layouts):
            layouts[self.current_layout_idx]["shortcut"] = val
            self.refresh_layout_combo()
            self.layout_combo.setCurrentIndex(self.current_layout_idx)

    def on_gap_changed(self, val):
        self.gap_val_lbl.setText(f"{val}px")
        self.config.setdefault("settings", {})["gap"] = val
        self.canvas.gap = val
        self.canvas.update()

    def on_margin_changed(self, val):
        self.margin_val_lbl.setText(f"{val}px")
        self.config.setdefault("settings", {})["margin"] = val
        self.canvas.margin = val
        self.canvas.update()

    def apply_template_by_id(self, template_id):
        for t in DEFAULT_LAYOUTS:
            if t["id"] == template_id:
                g = self.current_screen.get("geometry", {})
                w = g.get("width", 5120)
                h = g.get("height", 1440)
                self.canvas.set_layout_data(
                    t["zones"],
                    self.canvas.aspect_ratio,
                    w,
                    h,
                    self.canvas.gap,
                    self.canvas.margin
                )
                self.on_canvas_layout_changed()
                break

    def create_new_layout(self):
        count = len(self.config.get("layouts", [])) + 1
        new_layout = {
            "id": f"custom-{count}",
            "name": f"Custom Layout {count}",
            "description": "User custom created layout.",
            "shortcut": min(9, count),
            "zones": [
                [0.0, 0.0, 0.5, 1.0],
                [0.5, 0.0, 0.5, 1.0]
            ]
        }
        self.config.setdefault("layouts", []).append(new_layout)
        self.refresh_layout_combo()
        self.layout_combo.setCurrentIndex(len(self.config["layouts"]) - 1)

    def add_free_zone(self):
        self.canvas.zones.append([0.2, 0.2, 0.6, 0.6])
        self.canvas.selected_zone_index = len(self.canvas.zones) - 1
        self.canvas.update()
        self.on_canvas_layout_changed()

    def apply_to_current_screen(self):
        screen_name = self.current_screen.get("name", "DP-3")
        layouts = self.config.get("layouts", [])
        if 0 <= self.current_layout_idx < len(layouts):
            layout_id = layouts[self.current_layout_idx]["id"]
            self.config.setdefault("activeLayouts", {})[screen_name] = layout_id
            self.config["activeLayouts"]["default"] = layout_id
            save_config(self.config)
            QMessageBox.information(self, "FancyZones", f"Layout '{layouts[self.current_layout_idx]['name']}' applied to {screen_name}!")

    def save_and_apply(self):
        self.apply_to_current_screen()
        save_config(self.config)

    def install_to_top_bar(self):
        import subprocess
        subprocess.run(["bash", str(Path(__file__).parent.parent / "bin" / "install.sh")], capture_output=True)
        QMessageBox.information(self, "FancyZones", "FancyZones top bar widget and KWin snapping engine re-installed and enabled!")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FancyZones KDE")
    editor = FancyZonesEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
