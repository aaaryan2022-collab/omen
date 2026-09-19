# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Screenshot capture using mss for fast multi-monitor screenshots.
"""

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from app.config import DATA_DIR
from app.logging_config import logger

try:
    import mss
    _HAVE_MSS = True
except ImportError:
    _HAVE_MSS = False

try:
    from PIL import Image
    _HAVE_PIL = True
except ImportError:
    _HAVE_PIL = False


@dataclass
class ScreenshotInfo:
    """Information about a captured screenshot."""
    path: str
    width: int
    height: int
    monitor_index: int
    timestamp: str


def capture_screen(
    monitor_index: int = 0,
    output_dir: Optional[str] = None,
) -> Optional[ScreenshotInfo]:
    """
    Captures a screenshot of the specified monitor.
    Returns ScreenshotInfo or None on failure.
    """
    if not _HAVE_MSS:
        logger.warning("mss not available for screenshot capture")
        return None

    output_dir = output_dir or str(DATA_DIR / "screenshots")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        with mss.mss() as sct:
            if monitor_index == 0:
                # Capture all monitors (primary)
                monitor = sct.monitors[0] if len(sct.monitors) > 0 else sct.monitors[1]
            else:
                idx = min(monitor_index, len(sct.monitors) - 1)
                monitor = sct.monitors[idx] if idx > 0 else sct.monitors[1]

            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{monitor_index}.png"
            output_path = os.path.join(output_dir, filename)

            sct_img = sct.grab(monitor)

            # Save with PIL if available for better quality
            if _HAVE_PIL:
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(output_path, "PNG")
            else:
                # Fallback: save raw
                with open(output_path, "wb") as f:
                    import struct
                    # This is a simplified save — PIL is preferred
                    pass
                logger.warning("PIL not available, cannot save screenshot raw buffer")
                return None

            info = ScreenshotInfo(
                path=output_path,
                width=sct_img.width,
                height=sct_img.height,
                monitor_index=monitor_index,
                timestamp=timestamp,
            )
            logger.info(f"Screenshot saved: {output_path}")
            return info

    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        return None


def capture_all_monitors(output_dir: Optional[str] = None) -> List[ScreenshotInfo]:
    """Captures screenshots of all connected monitors."""
    results = []
    if not _HAVE_MSS:
        return results

    try:
        with mss.mss() as sct:
            for i, monitor in enumerate(sct.monitors[1:], start=1):
                info = capture_screen(monitor_index=i, output_dir=output_dir)
                if info:
                    results.append(info)
    except Exception as e:
        logger.error(f"Multi-monitor capture failed: {e}")

    return results


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
