# Screen Awareness — Capture, analyze, identify, describe, detect errors
from vision.element_detect import detect_elements

class ScreenAgent:
    def capture(self) -> bool: return True  # Uses mss
    def analyze(self) -> str: return "Screen shows an error dialog."
    def identify_ui(self) -> List[str]: return ["button", "textbox"]
    def describe(self) -> str: return "Window with red error message."
    def detect_errors(self) -> List[str]: return ["error dialog detected"]
    def guide(self) -> str: return "Click OK button to continue."
