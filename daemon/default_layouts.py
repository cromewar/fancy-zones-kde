"""
Built-in FancyZones layout templates with aspect-ratio recommendations and normalized zone coordinates.
Each zone is defined as [x, y, width, height] normalized between 0.0 and 1.0.
"""

DEFAULT_LAYOUTS = [
    {
        "id": "priority-grid",
        "name": "Priority Grid",
        "description": "50% Center Main Workspace with 25% Left and Right Sidebars. Ideal for 32:9 and 21:9.",
        "shortcut": 1,
        "recommendedRatios": ["32:9", "21:9", "16:9"],
        "zones": [
            [0.25, 0.0, 0.50, 1.0],     # 1: Center Main Priority Zone
            [0.0, 0.0, 0.25, 1.0],      # 2: Left column
            [0.75, 0.0, 0.25, 1.0]      # 3: Right column
        ]
    },
    {
        "id": "cols-3",
        "name": "3 Columns",
        "description": "Three equal vertical columns (~1706px on 5120x1440). Perfect for browsing + IDE + chat.",
        "shortcut": 2,
        "recommendedRatios": ["32:9", "21:9"],
        "zones": [
            [0.0, 0.0, 0.3333, 1.0],    # 1: Left column
            [0.3333, 0.0, 0.3334, 1.0], # 2: Middle column
            [0.6667, 0.0, 0.3333, 1.0]  # 3: Right column
        ]
    },
    {
        "id": "cols-4",
        "name": "4 Columns",
        "description": "Four equal vertical columns (1280px each). Tailored for 32:9 Super Ultrawide.",
        "shortcut": 3,
        "recommendedRatios": ["32:9"],
        "zones": [
            [0.0, 0.0, 0.25, 1.0],      # 1: Far left
            [0.25, 0.0, 0.25, 1.0],     # 2: Center left
            [0.50, 0.0, 0.25, 1.0],     # 3: Center right
            [0.75, 0.0, 0.25, 1.0]      # 4: Far right
        ]
    },
    {
        "id": "dual-split",
        "name": "Dual 16:9 Split",
        "description": "Two equal 50% halves (2560x1440 each). Effectively two 16:9 displays side-by-side.",
        "shortcut": 4,
        "recommendedRatios": ["32:9", "21:9", "16:9"],
        "zones": [
            [0.0, 0.0, 0.50, 1.0],      # 1: Left 50%
            [0.50, 0.0, 0.50, 1.0]      # 2: Right 50%
        ]
    },
    {
        "id": "ultrawide-master-4",
        "name": "Ultrawide Master + 4 Flanks",
        "description": "50% Center Workspace with 4 stacked side tiles (2 on left, 2 on right).",
        "shortcut": 5,
        "recommendedRatios": ["32:9", "21:9"],
        "zones": [
            [0.25, 0.0, 0.50, 1.0],     # 1: Center Master
            [0.0, 0.0, 0.25, 0.5],      # 2: Top-Left
            [0.0, 0.5, 0.25, 0.5],      # 3: Bottom-Left
            [0.75, 0.0, 0.25, 0.5],     # 4: Top-Right
            [0.75, 0.5, 0.25, 0.5]      # 5: Bottom-Right
        ]
    },
    {
        "id": "grid-3x2",
        "name": "Grid 3x2",
        "description": "Six zones in a 3x2 grid. Great for multi-dashboard workflows.",
        "shortcut": 6,
        "recommendedRatios": ["32:9", "21:9", "16:9"],
        "zones": [
            [0.0, 0.0, 0.3333, 0.5],    # 1: Top-Left
            [0.3333, 0.0, 0.3334, 0.5], # 2: Top-Center
            [0.6667, 0.0, 0.3333, 0.5], # 3: Top-Right
            [0.0, 0.5, 0.3333, 0.5],    # 4: Bottom-Left
            [0.3333, 0.5, 0.3334, 0.5], # 5: Bottom-Center
            [0.6667, 0.5, 0.3333, 0.5]  # 6: Bottom-Right
        ]
    },
    {
        "id": "grid-2x2",
        "name": "Grid 2x2",
        "description": "Four equal quadrants. The classic 4-zone multitasking grid.",
        "shortcut": 7,
        "recommendedRatios": ["16:9", "16:10", "3:2"],
        "zones": [
            [0.0, 0.0, 0.5, 0.5],       # 1: Top-Left
            [0.5, 0.0, 0.5, 0.5],       # 2: Top-Right
            [0.0, 0.5, 0.5, 0.5],       # 3: Bottom-Left
            [0.5, 0.5, 0.5, 0.5]        # 4: Bottom-Right
        ]
    },
    {
        "id": "rows-2",
        "name": "2 Rows",
        "description": "Two equal horizontal zones split top and bottom.",
        "shortcut": 8,
        "recommendedRatios": ["16:9", "9:16"],
        "zones": [
            [0.0, 0.0, 1.0, 0.5],       # 1: Top half
            [0.0, 0.5, 1.0, 0.5]        # 2: Bottom half
        ]
    },
    {
        "id": "focus",
        "name": "Focus Zone",
        "description": "Centered large workspace window with margins for distraction-free focus.",
        "shortcut": 9,
        "recommendedRatios": ["32:9", "21:9", "16:9"],
        "zones": [
            [0.20, 0.08, 0.60, 0.84]    # 1: Centered canvas
        ]
    }
]

DEFAULT_SETTINGS = {
    "gap": 8,
    "margin": 8,
    "holdShiftToSnap": True,
    "alwaysSnapOnDrag": False,
    "multiZoneSnap": True,
    "showOutline": True,
    "showZoneNumbers": True,
    "highlightColor": "#3daee9",
    "restoreOnUnsnap": True,
    "autoDetectAspectRatios": True
}
