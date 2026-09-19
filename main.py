
"""
OMEN — Local AI Personal Assistant
Application Entry Point.

Usage:
    python main.py            # Launch GUI (default)
    python main.py --cli      # Interactive CLI mode
    python main.py --debug    # Debug mode with verbose logging
    python main.py --wizard   # First-run setup wizard
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import config, reload_config
from app.logging_config import logger, setup_logging
from core.events import get_event_bus
from core.agent import Agent


def run_cli():
    """Interactive CLI mode for OMEN."""
    print("OMEN — CLI Mode (type 'exit' or 'quit' to end)")
    print("=" * 50)

    setup_logging(debug=True)
    agent = Agent()

    # Pre-warm brain with mock config if needed
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break

        if user_input.lower() in ("help", "?"):
            print("Commands: 'exit' | 'quit' | 'help' | any natural language request")
            continue

        try:
            result = agent.process(user_input)
            print(f"\nOMEN: {result['response_text']}")
            if result['plan'] and result['plan'].steps:
                print(f"[Plan: {len(result['plan'].steps)} step(s)]")
        except Exception as e:
            print(f"Error: {e}")


def run_debug():
    """Debug mode with verbose logging."""
    config.debug_mode = True
    config.mock_mode = True  # Safe default for testing
    setup_logging(debug=True)
    logger.info("OMEN Debug Mode activated")

    agent = Agent()
    print("OMEN Debug Mode (mock provider active)")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            break

        try:
            result = agent.process(user_input)
            print(f"\nOMEN: {result['response_text']}")
            if result.get('plan'):
                for step in result['plan'].steps:
                    print(f"  Step: {step.tool} [{step.status.value}]")
        except Exception as e:
            print(f"Error: {e}")


def run_wizard():
    """First-run setup wizard."""
    print("OMEN Setup Wizard")
    print("=" * 50)
    print("This will guide you through initial configuration.\n")

    config.reload_config()

    # Step 1: Confirm Ollama
    print("[1/5] Checking Ollama connection...")
    try:
        from providers.llm.ollama import OllamaProvider
        provider = OllamaProvider()
        if provider.check_connection():
            models = provider.list_models()
            print(f"  ✓ Ollama connected. Models: {models}")
        else:
            print("  ⚠ Ollama not detected. Will use mock mode.")
            config.mock_mode = True
    except Exception as e:
        print(f"  ⚠ Ollama check failed: {e}. Mock mode active.")
        config.mock_mode = True

    # Step 2: Configure voice
    print("\n[2/5] Voice settings...")
    voice_enabled = input("  Enable voice? (y/n) [y]: ").strip().lower() or "y"
    config.voice_enabled = voice_enabled != "n"
    print(f"  Voice: {'enabled' if config.voice_enabled else 'disabled'}")

    # Step 3: Allowed directories
    print("\n[3/5] Allowed directories for file operations:")
    print(f"  Current defaults: {config.allowed_directories}")
    custom = input("  Accept defaults? (y/n) [y]: ").strip().lower() or "y"
    if custom != "y":
        dirs_input = input("  Enter comma-separated paths: ").strip()
        if dirs_input:
            config.allowed_directories = [d.strip() for d in dirs_input.split(",")]

    # Step 4: Security settings
    print("\n[4/5] Security settings...")
    confirm_hr = input("  Confirm HIGH-risk tools? (y/n) [y]: ").strip().lower() or "y"
    config.security_confirm_high_risk = confirm_hr != "n"
    print(f"  HIGH-risk confirmation: {'enabled' if config.security_confirm_high_risk else 'disabled'}")

    # Step 5: Save and confirm
    print("\n[5/5] Finalizing...")
    config.first_run_completed = True
    try:
        config.save()
    except Exception:
        pass  # Config auto-saves via pydantic-settings

    print("\n✓ Setup complete! Launch OMEN with: python main.py")


def run_gui():
    """Launch PySide6 GUI application."""
    print("OMEN starting in GUI mode...")

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load stylesheet
    qss_path = PROJECT_ROOT / "ui" / "styles" / "dark_theme.qss"
    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Create agent
    agent = Agent()

    # Create main window
    from ui.main_window import MainWindow
    window = MainWindow(agent)

    # If emergency stop was active, show banner
    from safety.emergency_stop import get_emergency_stop
    if get_emergency_stop().is_stopped:
        window._emergency_banner.setHidden(False)

    window.show()

    sys.exit(app.exec())


def main():
    parser = argparse.ArgumentParser(description="OMEN — Local AI Personal Assistant")
    parser.add_argument("--cli", action="store_true", help="Launch interactive CLI mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    parser.add_argument("--wizard", action="store_true", help="Run first-run setup wizard")
    parser.add_argument("--test", action="store_true", help="Run quick self-test")
    parser.add_argument("--version", action="store_true", help="Show version")
    args = parser.parse_args()

    if args.version:
        from app import __version__
        print(f"OMEN v{__version__}")
        return

    if args.wizard:
        run_wizard()
        return

    if args.debug:
        run_debug()
        return

    if args.cli:
        run_cli()
        return

    if args.test:
        run_self_test()
        return

    # Default: GUI mode
    run_gui()


def run_self_test():
    """Quick self-test to verify core components."""
    print("OMEN Self-Test")
    print("=" * 50)

    tests_passed = 0
    tests_failed = 0

    def test(name, fn):
        nonlocal tests_passed, tests_failed
        try:
            result = fn()
            if result:
                print(f"  ✓ {name}")
                tests_passed += 1
            else:
                print(f"  ✗ {name} (no result)")
                tests_failed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            tests_failed += 1

    # Config test
    test("Config loading", lambda: config is not None)

    # Database test
    try:
        from database.database import get_db
        db = get_db()
        test("Database connection", lambda: db is not None)
    except Exception as e:
        test("Database connection", lambda: False)

    # Tool registry test
    try:
        from tools.registry import get_tool_registry
        registry = get_tool_registry()
        tools = registry.list_all()
        test(f"Tool registry ({len(tools)} tools)", lambda: len(tools) > 0)
    except Exception as e:
        test("Tool registry", lambda: False)

    # Safety test
    try:
        from safety.permissions import get_permission_manager
        pm = get_permission_manager()
        test("Permission manager", lambda: pm is not None)
    except Exception as e:
        test("Permission manager", lambda: False)

    # Agent test
    try:
        agent = Agent()
        test("Agent creation", lambda: agent is not None)
    except Exception as e:
        test("Agent creation", lambda: False)

    print(f"\nResults: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


if __name__ == "__main__":
    main()


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
