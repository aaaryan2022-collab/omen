import pytest
from core.skills.skills_registry import skills_registry, Skill
from core.research.deep_research import deep_research_agent
from core.traces.trace_collector import trace_collector, ExecutionTrace
from core.mcp.mcp_client import mcp_manager


def test_skills_registry():
    all_skills = skills_registry.list_all()
    assert len(all_skills) >= 4
    names = [s.name for s in all_skills]
    assert "python_debugging" in names
    assert "deep_research" in names

    # Test custom skill registration
    custom = Skill(
        name="test_skill",
        description="Testing skill",
        category="testing",
        instructions="Always write assertions."
    )
    skills_registry.register(custom)
    assert skills_registry.get("test_skill") is not None


def test_deep_research():
    report = deep_research_agent.conduct_research("Quantum Computing Basics", max_sources=2)
    assert report.topic == "Quantum Computing Basics"
    assert "Executive Summary" in report.full_markdown
    assert len(report.findings) >= 1


def test_trace_collector():
    trace = ExecutionTrace(
        trace_id="test_trace_1",
        timestamp=123456.0,
        prompt="hello omen",
        agent_name="orchestrator",
        latency_ms=42.5,
        success=True,
        response_summary="Hello there"
    )
    trace_collector.record_trace(trace)
    recent = trace_collector.list_recent()
    assert any(t.trace_id == "test_trace_1" for t in recent)
    stats = trace_collector.get_summary_stats()
    assert stats["total_traces"] >= 1
