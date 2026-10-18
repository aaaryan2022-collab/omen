# Feature Gap Report

Per Protocol Section 79, this report documents features where external platform dependencies or hardware runtimes are optional:

| Feature / Capability | Status | Blocker / Dependency | Recommended Resolution |
|---|---|---|---|
| **Tesseract OCR Binary** | Optional Runtime | `tesseract.exe` not currently in system PATH | Install Tesseract OCR for Windows (`winget install UB-Mannheim.TesseractOCR`) to enable local pixel-level OCR alongside existing screenshot vision analysis. |
| **PyQt6 System Display** | Headless CLI / Local GUI | PyQt6 GUI runs on active Windows desktop display session; headless CLI (`omen doctor`, `omen ask`) runs independently. | Use `python main.py` in interactive desktop session; `python cli/main.py` for terminal and remote sessions. |

No architectural or functional feature gaps remain. All feasible user-facing capabilities across the five reference systems are implemented.
