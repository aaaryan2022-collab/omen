# ============================================
"""
Traces package for OMEN.
"""

from core.traces.trace_collector import (
    ExecutionTrace,
    ToolCallRecord,
    TraceCollector,
    trace_collector,
)

__all__ = [
    "ExecutionTrace",
    "ToolCallRecord",
    "TraceCollector",
    "trace_collector",
]
