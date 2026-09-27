"""On-demand local screen analysis through Ollama vision models."""

import base64
import json
import re
from typing import Optional

import mss
from pydantic import BaseModel, Field

from app.config import config
from app.constants import RiskLevel
from app.logging_config import logger
from tools.base import BaseTool, ToolResult


class AnalyzeScreenArgs(BaseModel):
    prompt: str = Field(default="Describe what is on the screen.", max_length=1000)
    monitor: int = Field(default=1, ge=0, le=8)


class ClickTargetArgs(BaseModel):
    target: str = Field(min_length=1, max_length=200, description="Visible button, control, or text to click")
    monitor: int = Field(default=1, ge=0, le=8)


def capture_screen_base64(monitor: int = 1) -> tuple[str, int, int]:
    """Capture one monitor without writing temporary image files."""
    with mss.mss() as screen:
        index = monitor if monitor < len(screen.monitors) else 1
        image = screen.grab(screen.monitors[index])
        png_bytes = mss.tools.to_png(image.rgb, image.size)
    return base64.b64encode(png_bytes).decode("ascii"), image.width, image.height


def analyze_screen(prompt: str = "Describe what is on the screen.", monitor: int = 1) -> str:
    """Ask the configured local Ollama vision model about the current screen."""
    from providers.llm.ollama import OllamaProvider
    import requests

    encoded, width, height = capture_screen_base64(monitor)
    provider = OllamaProvider(model=config.ollama_vision_model, auto_select_model=False)
    installed_models = provider.list_models()
    if provider.model not in installed_models:
        raise RuntimeError(
            f"Vision model '{provider.model}' is not installed. Install it with Ollama before using screen analysis."
        )
    response = requests.post(
        f"{provider.base_url}/api/generate",
        json={
            "model": provider.model,
            "prompt": prompt,
            "images": [encoded],
            "stream": False,
            "options": {
                "num_ctx": config.ollama_context_tokens,
                "num_predict": config.ollama_max_output_tokens,
            },
        },
        timeout=provider.timeout,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama vision returned HTTP {response.status_code}")
    result = response.json().get("response", "").strip()
    if not result:
        raise RuntimeError("Ollama vision returned an empty response")
    logger.info("Screen analyzed at %sx%s with %s", width, height, provider.model)
    return result


def locate_screen_target(target: str, monitor: int = 1) -> tuple[int, int]:
    """Ask the vision model for the center coordinate of a visible target."""
    from providers.llm.ollama import OllamaProvider
    import requests

    encoded, width, height = capture_screen_base64(monitor)
    provider = OllamaProvider(model=config.ollama_vision_model, auto_select_model=False)
    if provider.model not in provider.list_models():
        raise RuntimeError(f"Vision model '{provider.model}' is not installed.")
    prompt = (
        f"Find the visible target named '{target}'. Return only JSON in this exact form: "
        '{"x": 123, "y": 456, "confidence": 0.0}. '
        "Coordinates must be pixels in the supplied image. Return x=-1,y=-1 if absent."
    )
    response = requests.post(
        f"{provider.base_url}/api/generate",
        json={"model": provider.model, "prompt": prompt, "images": [encoded], "stream": False,
              "options": {"num_ctx": config.ollama_context_tokens, "num_predict": 128}},
        timeout=provider.timeout,
    )
    response.raise_for_status()
    text = response.json().get("response", "")
    match = re.search(r"\{.*?\}", text, flags=re.DOTALL)
    if not match:
        raise RuntimeError("Vision model did not return target coordinates.")
    coordinates = json.loads(match.group(0))
    x, y = int(coordinates.get("x", -1)), int(coordinates.get("y", -1))
    confidence = float(coordinates.get("confidence", 0.0))
    if x < 0 or y < 0 or x >= width or y >= height or confidence < 0.65:
        raise RuntimeError(f"Target '{target}' was not located with sufficient confidence.")
    return x, y


class AnalyzeScreenTool(BaseTool):
    name = "analyze_screen"
    description = "Captures the screen on demand and describes it with a local Ollama vision model."
    risk_level = RiskLevel.MEDIUM
    permission_tag = "screen_awareness"
    args_schema = AnalyzeScreenArgs

    def execute(self, prompt: str = "Describe what is on the screen.", monitor: int = 1, **kwargs) -> ToolResult:
        try:
            result = analyze_screen(prompt=prompt, monitor=monitor)
            return ToolResult(success=True, data={"analysis": result}, message=result)
        except Exception as exc:
            logger.error("Screen analysis failed: %s", exc)
            return ToolResult(success=False, error=str(exc), message="Screen analysis is unavailable.")


class ClickScreenTargetTool(BaseTool):
    name = "click_screen_target"
    description = "Uses local vision to locate a named visible target and click it. Requires confirmation."
    risk_level = RiskLevel.HIGH
    permission_tag = "desktop_automation"
    args_schema = ClickTargetArgs

    def execute(self, target: str, monitor: int = 1, **kwargs) -> ToolResult:
        try:
            from automation.mouse import click_mouse

            x, y = locate_screen_target(target, monitor)
            if not click_mouse(x, y):
                return ToolResult(success=False, error="Emergency stop active", message="Click cancelled.")
            return ToolResult(success=True, data={"target": target, "x": x, "y": y}, message=f"Clicked '{target}' at ({x}, {y}).")
        except Exception as exc:
            logger.error("Visual click failed: %s", exc)
            return ToolResult(success=False, error=str(exc), message="Visual click failed safely.")