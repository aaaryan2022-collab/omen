# ============================================
"""
Execution Trace Collector for OMEN.
Records structured logs of prompts, model usage, tool calls, latency, and results.
"""

import time
import os
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.logging_config import logger


class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    success: bool
    latency_ms: float
    error: Optional[str] = None


class ExecutionTrace(BaseModel):
    trace_id: str
    timestamp: float
    prompt: str
    model_name: Optional[str] = None
    agent_name: str = "orchestrator"
    latency_ms: float
    total_tokens: Optional[int] = None
    tools_called: List[ToolCallRecord] = Field(default_factory=list)
    success: bool
    response_summary: str
    error: Optional[str] = None


class TraceCollector:
    """Manages persistent execution traces."""

    def __init__(self, log_path: str = "logs/traces.jsonl"):
        self.log_path = os.path.abspath(log_path)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._in_memory_traces: List[ExecutionTrace] = []

    def record_trace(self, trace: ExecutionTrace) -> None:
        self._in_memory_traces.append(trace)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(trace.model_dump_json() + "\n")
            logger.debug(f"Recorded trace: {trace.trace_id} ({trace.latency_ms:.1f}ms)")
        except Exception as e:
            logger.error(f"Failed to write trace log: {e}")

    def list_recent(self, limit: int = 50) -> List[ExecutionTrace]:
        return self._in_memory_traces[-limit:]

    def get_summary_stats(self) -> Dict[str, Any]:
        count = len(self._in_memory_traces)
        if count == 0:
            return {"total_traces": 0, "success_rate": 1.0, "avg_latency_ms": 0.0}
        successes = sum(1 for t in self._in_memory_traces if t.success)
        avg_lat = sum(t.latency_ms for t in self._in_memory_traces) / count
        return {
            "total_traces": count,
            "success_rate": successes / count,
            "avg_latency_ms": round(avg_lat, 2)
        }


trace_collector = TraceCollector()
