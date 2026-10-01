"""Vision / screen analysis layer — screenshot, OCR, perception."""
from typing import Optional, Dict, Any, List
import json
from mss import mss
from PIL import Image
from app.logging_config import logger


class VisionModule:
    """Screen capture + basic text extraction (PIL + optional OCR fallback)."""

    def __init__(self):
        self._sct = mss()
        self.modes = {
            "screenshot":"on_demand",
            "region":"on_region",
            "window":"active",
            "periodic":"none",
            "continuous":"disabled",
        }

    def screenshot(self, region: Optional[Dict[str, int]] = None) -> Optional[Image.Image]:
        try:
            with self._sct.grab(region or self._sct.monitors[-1]) as img:
                return Image.frombytes("RGB", img.size, img.rgb)
        except Exception as exc:
            logger.error(f"Vision screenshot failed: {exc}")
            return None

    def describe_active_window(self) -> str:
        # Placeholder: real version integrates core agent + screen text
        return "Active window visible; perception relies on available vision model."

    def extract_text(self, img: Image.Image) -> List[str]:
        # Placeholder: integrate pytesseract / vision LLM when installed
        return ["Text extraction requires vision model integration."]

    def confidence(self) -> float:
        return 0.0  # No visual model active
