# ============================================
"""
Screenshot capture using mss for fast multi-monitor screenshots.
"""

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from app.constants import DATA_DIR
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

            # Save with PIL if available, or native mss tools
            if _HAVE_PIL:
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(output_path, "PNG")
            else:
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_path)

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


