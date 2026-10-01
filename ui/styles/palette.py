# ============================================
"""
OMEN UI color palette and design tokens.
Holographic Cyberpunk / 3D Depth / Glassmorphism aesthetic.
"""

# Primary Holographic Cyan / Teal Colors
PRIMARY = "#00F0FF"           # Laser Cyan (OMEN Core)
PRIMARY_DARK = "#00A3B4"
PRIMARY_LIGHT = "#70FAFF"
PRIMARY_GLOW = "rgba(0, 240, 255, 0.35)"
PRIMARY_DIM = "rgba(0, 240, 255, 0.08)"

# Secondary Neon Violet / Purple Accents
SECONDARY = "#7000FF"         # Arc Violet
SECONDARY_LIGHT = "#A355FF"
SECONDARY_GLOW = "rgba(112, 0, 255, 0.35)"
SECONDARY_DIM = "rgba(112, 0, 255, 0.08)"

# Tertiary Neon Pink / Magenta
TERTIARY = "#FF00AA"          # Holographic Magenta
TERTIARY_LIGHT = "#FF5EC9"
TERTIARY_DIM = "rgba(255, 0, 170, 0.08)"

# Background & Surface Hierarchy (Deep Obsidian Space)
BACKGROUND_DARK = "#060A11"    # Deep Space Background
BACKGROUND_MEDIUM = "#0B1019"  # Panel Surface
BACKGROUND_CARD = "#101824"    # Raised Glass Card
BACKGROUND_HOVER = "#182030"   # Hover Highlight
BACKGROUND_ACTIVE = "#203048"  # Active State
BORDER = "#1C2A42"             # Subtle Sci-Fi Border
BORDER_ACTIVE = "#00F0FF"      # Active Glowing Border

# Text Colors
TEXT_PRIMARY = "#F1F5F9"       # Crisp White
TEXT_SECONDARY = "#94A3B8"     # Muted Slate
TEXT_DIM = "#64748B"           # Dimmed / Code
TEXT_ACCENT = "#00F0FF"        # Cyber Cyan Accent
TEXT_GLOW = "0 0 10px rgba(0, 240, 255, 0.7)"
TEXT_GLOW_VIOLET = "0 0 10px rgba(112, 0, 255, 0.7)"
TEXT_GLOW_MAGENTA = "0 0 10px rgba(255, 0, 170, 0.7)"

# Status Tiers
SUCCESS = "#00FF9D"            # Neon Green
WARNING = "#FFB703"            # Amber Gold
ERROR = "#FF0055"              # Cyber Red / Coral
INFO = "#00F0FF"               # Cyan
STOP = "#EF4444"               # Emergency Alert

# Special Effects
GLASS_BACKGROUND = "rgba(16, 24, 36, 0.78)"
GLASS_BORDER = "1px solid rgba(0, 240, 255, 0.22)"
GLASS_BORDER_VIOLET = "1px solid rgba(112, 0, 255, 0.25)"
BOX_GLOW = "0px 0px 20px rgba(0, 240, 255, 0.25)"
ARC_GLOW = "0px 0px 35px rgba(0, 240, 255, 0.45)"
HOLOGRAPHIC_SHADOW = "0 0 20px rgba(0,240,255,0.18), 0 0 60px rgba(0,240,255,0.08), inset 0 0 20px rgba(0,240,255,0.05)"
VOXEL_DEPTH = "0 2px 4px rgba(0,0,0,0.6), 0 8px 24px rgba(0,0,0,0.4), 0 0 1px rgba(0,240,255,0.2)"

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"
FONT_HEADER = "Segoe UI Semibold"
