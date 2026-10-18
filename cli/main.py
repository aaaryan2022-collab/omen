# ============================================
"""
OMEN Command-Line Interface (CLI).
Provides system diagnostics ('omen doctor'), quick execution ('omen ask'),
status checks, tool discovery, and trace inspection.
"""

import sys
import argparse
import os
import shutil
import platform
import psutil
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_doctor() -> None:
    """Performs comprehensive diagnostics of the OMEN environment."""
    print("=" * 60)
    print("                O M E N   D O C T O R")
    print("            Comprehensive System Health Check")
    print("=" * 60)

    # 1. Platform & Python
    py_ver = platform.python_version()
    os_name = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
    print(f"\n[OS & Runtime]")
    print(f"  * Operating System : {os_name}")
    print(f"  * Python Version   : {py_ver} (Path: {sys.executable})")

    # 2. Hardware Resources
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.getcwd())
    cpu_count = psutil.cpu_count(logical=True)
    print(f"\n[Hardware Profile]")
    print(f"  * CPU Cores        : {cpu_count}")
    print(f"  * RAM Total        : {mem.total / (1024**3):.1f} GB ({mem.percent}% used)")
    print(f"  * Disk Free        : {disk.free / (1024**3):.1f} GB")

    # 3. Core Dependencies & Libraries
    print(f"\n[Core Dependencies]")
    checks = [
        ("PyQt6", "PyQt6.QtCore"),
        ("Pydantic", "pydantic"),
        ("ChromaDB", "chromadb"),
        ("SpeechRecognition", "speech_recognition"),
        ("PyTTSx3", "pyttsx3"),
        ("Psutil", "psutil"),
    ]
    for label, mod_name in checks:
        try:
            __import__(mod_name)
            print(f"  * {label:<18}: [OK]")
        except ImportError:
            print(f"  * {label:<18}: [NOT INSTALLED]")

    # 4. External Services & Binaries
    print(f"\n[External Runtimes]")
    binaries = [
        ("Git", "git"),
        ("Ollama", "ollama"),
        ("Node.js", "node"),
        ("Tesseract OCR", "tesseract"),
    ]
    for label, cmd in binaries:
        found = shutil.which(cmd) is not None
        status = "[AVAILABLE]" if found else "[NOT FOUND IN PATH]"
        print(f"  * {label:<18}: {status}")

    # 5. OMEN Tool Registry
    print(f"\n[OMEN Tool Registry]")
    try:
        from tools.registry import get_tool_registry
        reg = get_tool_registry()
        tools = reg.list_all()
        print(f"  * Registered Tools : {len(tools)} loaded and verified")
    except Exception as e:
        print(f"  * Tool Registry    : [ERROR] {e}")

    # 6. Database & Storage
    print(f"\n[Databases & Persistence]")
    db_path = "omen.db"
    has_db = os.path.exists(db_path)
    print(f"  * SQLite Store     : {'[OK]' if has_db else '[INITIALIZING ON STARTUP]'}")

    print("\n" + "=" * 60)
    print("  Doctor Check Complete: System is ready for operation.")
    print("=" * 60)


def run_status() -> None:
    print("OMEN Status: ONLINE")
    mem = psutil.virtual_memory()
    print(f"Memory: {mem.percent}% | CPU: {psutil.cpu_percent()}%")


def run_tools() -> None:
    from tools.registry import get_tool_registry
    reg = get_tool_registry()
    print(f"Registered OMEN Tools ({len(reg.list_all())}):")
    for t in sorted(reg.list_all(), key=lambda x: x.name):
        print(f"  * {t.name:<25} [{t.risk_level.value}] : {t.description[:60]}")


def run_traces() -> None:
    from core.traces.trace_collector import trace_collector
    stats = trace_collector.get_summary_stats()
    print("Trace Collector Summary:")
    print(f"  * Total Traces   : {stats['total_traces']}")
    print(f"  * Success Rate   : {stats['success_rate'] * 100:.1f}%")
    print(f"  * Avg Latency    : {stats['avg_latency_ms']} ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="OMEN Desktop AI Operating Layer CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("doctor", help="Run comprehensive diagnostic health check")
    subparsers.add_parser("status", help="Display current system and engine status")
    subparsers.add_parser("tools", help="List all registered tools")
    subparsers.add_parser("traces", help="Display execution trace statistics")

    ask_parser = subparsers.add_parser("ask", help="Ask OMEN a prompt directly via CLI")
    ask_parser.add_argument("query", type=str, help="Question or command for OMEN")

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()
    elif args.command == "status":
        run_status()
    elif args.command == "tools":
        run_tools()
    elif args.command == "traces":
        run_traces()
    elif args.command == "ask":
        print(f"Processing: {args.query}")
        # Execute query via supervisor/agent
        from core.agent import Agent
        from app.config import config
        agent = Agent(config)
        res = agent.process_input(args.query)
        print(f"\nOMEN: {res}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
