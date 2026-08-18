import math
from typing import Tuple, Dict, Any, List

def calculate_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def detect_aspect_ratio(width: int, height: int) -> Dict[str, Any]:
    """
    Calculates the exact and common standard aspect ratio for a given resolution.
    Returns ratio string (e.g. '32:9', '21:9', '16:9'), category name, and decimal value.
    """
    if width <= 0 or height <= 0:
        return {"ratio": "16:9", "name": "Unknown", "decimal": 1.777, "category": "standard"}
    
    decimal = width / height
    
    # Common standard aspect ratios with tolerance
    known_ratios = [
        (32 / 9, "32:9", "Super Ultrawide"),
        (43 / 18, "43:18", "Super Ultrawide"),
        (21 / 9, "21:9", "Ultrawide"),
        (12 / 5, "24:10", "Ultrawide"),
        (64 / 27, "21.3:9", "Ultrawide"),
        (16 / 9, "16:9", "Standard Widescreen"),
        (16 / 10, "16:10", "Productivity / Laptop"),
        (3 / 2, "3:2", "Surface / Classic"),
        (4 / 3, "4:3", "Standard Classic"),
        (5 / 4, "5:4", "Classic"),
        (1 / 1, "1:1", "Square"),
        (9 / 16, "9:16", "Vertical Portrait"),
        (10 / 16, "10:16", "Vertical Productivity"),
        (9 / 21, "9:21", "Vertical Ultrawide"),
        (9 / 32, "9:32", "Vertical Super Ultrawide")
    ]
    
    closest_match = None
    min_diff = 999.0
    
    for r_val, r_name, cat_name in known_ratios:
        diff = abs(decimal - r_val)
        if diff < min_diff:
            min_diff = diff
            closest_match = (r_name, cat_name)
    
    # If difference is close enough (within 5%), use standard name, otherwise compute GCD
    if closest_match and min_diff < 0.08:
        ratio_str, category_str = closest_match
    else:
        gcd = calculate_gcd(width, height)
        rw = width // gcd
        rh = height // gcd
        # If numbers are huge, round to approximation
        if rw > 50 or rh > 50:
            ratio_str = f"{decimal:.2f}:1"
        else:
            ratio_str = f"{rw}:{rh}"
        category_str = "Custom"
    
    return {
        "width": width,
        "height": height,
        "decimal": round(decimal, 3),
        "ratio": ratio_str,
        "name": category_str,
        "badge": f"{ratio_str} {category_str}"
    }

def compute_zone_pixels(zone_norm: List[float], screen_rect: Dict[str, int], gap: int = 8, margin: int = 8) -> Dict[str, int]:
    """
    Transforms normalized [x, y, w, h] coordinates (0.0 to 1.0) into pixel coordinates
    relative to the usable screen work area with outer margins and inner gaps.
    """
    sx = screen_rect["x"] + margin
    sy = screen_rect["y"] + margin
    sw = screen_rect["width"] - (2 * margin)
    sh = screen_rect["height"] - (2 * margin)
    
    zx, zy, zw, zh = zone_norm
    
    # Absolute inner box without gaps
    px = sx + int(round(zx * sw))
    py = sy + int(round(zy * sh))
    pw = int(round(zw * sw))
    ph = int(round(zh * sh))
    
    # Apply half gap to inner borders
    half_gap = gap // 2
    
    # Adjust for inner gaps
    final_x = px + (half_gap if zx > 0.001 else 0)
    final_y = py + (half_gap if zy > 0.001 else 0)
    final_w = pw - (half_gap if zx > 0.001 else 0) - (half_gap if (zx + zw) < 0.999 else 0)
    final_h = ph - (half_gap if zy > 0.001 else 0) - (half_gap if (zy + zh) < 0.999 else 0)
    
    return {
        "x": max(screen_rect["x"], final_x),
        "y": max(screen_rect["y"], final_y),
        "width": max(50, final_w),
        "height": max(50, final_h)
    }
