#!/usr/bin/env python3
"""
FancyZones Background Core & Utilities
Handles layout definitions, JSON configs, screen detection, and geometry conversions.
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "daemon"))

from default_layouts import DEFAULT_LAYOUTS, DEFAULT_SETTINGS
from utils import detect_aspect_ratio, compute_zone_pixels

CONFIG_DIR = Path.home() / ".config" / "fancyzones"
CONFIG_FILE = CONFIG_DIR / "config.json"
KWINRC_FILE = Path.home() / ".config" / "kwinrc"

SHORTCUT_MAP = {
    "priority-grid": 1,
    "cols-3": 2,
    "cols-4": 3,
    "dual-split": 4,
    "ultrawide-master-4": 5,
    "grid-3x2": 6,
    "grid-2x2": 7,
    "rows-2": 8,
    "focus": 9
}

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "layouts" not in data or not data["layouts"]:
                    data["layouts"] = DEFAULT_LAYOUTS
                if "settings" not in data:
                    data["settings"] = DEFAULT_SETTINGS
                return data
        except Exception as e:
            print(f"Error reading config: {e}")
    return init_config()

def init_config() -> Dict[str, Any]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    screens = get_connected_screens()
    active_layouts = {"default": "priority-grid"}
    for s in screens:
        name = s.get("name", "Display")
        g = s.get("geometry", {})
        ratio = g.get("width", 1920) / max(1, g.get("height", 1080))
        if ratio > 3.0:
            active_layouts[name] = "priority-grid"
        elif ratio > 2.0:
            active_layouts[name] = "cols-3"
        elif ratio < 0.8:
            active_layouts[name] = "rows-2"
        else:
            active_layouts[name] = "grid-2x2"

    cfg = {
        "version": "1.0.0",
        "settings": DEFAULT_SETTINGS,
        "activeLayouts": active_layouts,
        "layouts": DEFAULT_LAYOUTS
    }
    save_config(cfg)
    return cfg

def save_config(config_data: Dict[str, Any]) -> bool:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_connected_screens() -> List[Dict[str, Any]]:
    screens = []
    try:
        res = subprocess.run(["kscreen-doctor", "-j"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            for out in data.get("outputs", []):
                if out.get("connected") and out.get("enabled"):
                    mode = out.get("currentMode", {})
                    size = mode.get("size", {})
                    w = size.get("width", 1920)
                    h = size.get("height", 1080)
                    pos = out.get("pos", {})
                    screens.append({
                        "id": str(out.get("id", "1")),
                        "name": out.get("name", "Display"),
                        "geometry": {
                            "x": pos.get("x", 0),
                            "y": pos.get("y", 0),
                            "width": w,
                            "height": h
                        },
                        "aspectRatio": detect_aspect_ratio(w, h),
                        "primary": out.get("primary", False)
                    })
    except Exception as e:
        print(f"Error querying kscreen-doctor: {e}")

    if not screens:
        screens.append({
            "id": "1",
            "name": "DP-3",
            "geometry": {"x": 0, "y": 0, "width": 5120, "height": 1440},
            "aspectRatio": detect_aspect_ratio(5120, 1440),
            "primary": True
        })
    return screens
