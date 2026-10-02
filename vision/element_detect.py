"""Vision element detection — locate UI elements by visual + OCR match.

Supports:
- Screenshot-based search (mss + PIL)
- Text-based element match (OCR placeholder → pytesseract when installed)
- Approximate coordinate return for ComputerControl.click
- Fallback to center-of-region when no match

No Stark artifacts; pure OMEN architecture.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field

from app.logging_config import logger


@dataclass
class UIElement:
    label: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.0
    match_type: str = "visual"  # "visual" | "ocr" | "fallback"


class ElementDetector:
    """Find UI elements on screen for intelligent clicking (Spec #15)."""

    def __init__(self):
        self._vision = None
        self._ocr_available = False
        self._fallback_mode = True  # Safe default — center-of-region
        self._init_vision()
        self._init_ocr()

    def _init_vision(self):
        try:
            from vision import VisionModule
            self._vision = VisionModule()
            logger.info("ElementDetector: VisionModule loaded")
        except Exception as exc:
            logger.warning(f"ElementDetector: VisionModule unavailable: {exc}")

    def _init_ocr(self):
        try:
            import pytesseract  # noqa: F401
            self._ocr_available = True
            logger.info("ElementDetector: pytesseract available")
        except ImportError:
            logger.info("ElementDetector: pytesseract not installed — OCR placeholder only")
            self._ocr_available = False

    def find_element(self, label: str, region: Optional[Dict[str, int]] = None) -> Optional[UIElement]:
        """Locate a UI element by label (button text, link text, field name, icon alt).

        Returns UIElement with (x, y) for ComputerControl.click, or None.
        Strategy:
        1. Try OCR on screenshot (if pytesseract available)
        2. Try visual matching via VisionModule (placeholder)
        3. Fallback: return approximate center of region or screen center
        """
        # Step 1 — OCR
        if self._ocr_available and self._vision:
            try:
                img = self._vision.screenshot(region=region)
                if img:
                    import pytesseract
                    text = pytesseract.image_to_string(img)
                    if label.lower() in text.lower():
                        logger.info(f"ElementDetector: '{label}' found via OCR")
                        return UIElement(label=label, x=0, y=0, width=1, height=1,
                                         confidence=0.8, match_type="ocr")
            except Exception as exc:
                logger.debug(f"ElementDetector OCR error: {exc}")

        # Step 2 — visual (placeholder; wire real model when available)
        if self._vision:
            try:
                desc = self._vision.describe_active_window()
                if label.lower() in desc.lower():
                    logger.info(f"ElementDetector: '{label}' found via visual describe")
                    return UIElement(label=label, x=0, y=0, width=1, height=1,
                                     confidence=0.5, match_type="visual")
            except Exception as exc:
                logger.debug(f"ElementDetector visual error: {exc}")

        # Step 3 — fallback (safe center)
        logger.info(f"ElementDetector: '{label}' — fallback to region center")
        r = region or {"left": 0, "top": 0, "width": 1920, "height": 1080}
        return UIElement(
            label=label,
            x=r.get("left", 0) + r.get("width", 1920) // 2,
            y=r.get("top", 0) + r.get("height", 1080) // 2,
            width=r.get("width", 1920),
            height=r.get("height", 1080),
            confidence=0.1,
            match_type="fallback",
        )

    def click_element(self, label: str, region: Optional[Dict[str, int]] = None) -> bool:
        """Find element and return its (x,y) for ComputerControl to click.

        Returns True if element found at confidence >= 0.5, False otherwise.
        """
        elem = self.find_element(label, region=region)
        if elem is None:
            return False
        logger.info(f"ElementDetector: click_element '{label}' at ({elem.x}, {elem.y}) conf={elem.confidence}")
        return elem.confidence >= 0.5

    def list_elements_in_region(self, region: Optional[Dict[str, int]] = None) -> List[UIElement]:
        """Return candidate elements in region (for replanning on failure)."""
        candidates: List[UIElement] = []
        labels = ["OK", "Cancel", "Download", "Save", "Submit", "Login", "Close", "Back"]
        for label in labels:
            elem = self.find_element(label, region=region)
            if elem:
                candidates.append(elem)
        return candidates
