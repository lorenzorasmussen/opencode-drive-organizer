# tests/test_ai_orchestrator.py
"""
Test-driven development for Task 13: AI Orchestrator
"""

import pytest
import sys

sys.path.insert(0, "..")
from src.ai_orchestrator import AIOrchestrator


def test_orchestrator_initialization():
    """Verify orchestrator initialization"""
    orchestrator = AIOrchestrator()
    assert orchestrator is not None
    assert hasattr(orchestrator, "agents")


def test_register_agent():
    """Verify registering agents"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("duplicate_detector", lambda: {"status": "ready"})

    assert "duplicate_detector" in orchestrator.agents


def test_execute_agent():
    """Verify executing agent"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("test_agent", lambda: {"result": "success"})

    result = orchestrator.execute_agent("test_agent")

    assert result["status"] == "success"
    assert result["output"]["result"] == "success"


def test_workflow_execution():
    """Verify executing workflows"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("agent1", lambda: {"step1": "done"})
    orchestrator.register_agent("agent2", lambda: {"step2": "done"})

    workflow = ["agent1", "agent2"]
    results = orchestrator.execute_workflow(workflow)

    assert len(results) == 2


def test_parallel_execution():
    """Verify parallel agent execution"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("agent1", lambda: {"result": "1"})
    orchestrator.register_agent("agent2", lambda: {"result": "2"})

    agents = ["agent1", "agent2"]
    results = orchestrator.execute_parallel(agents)

    assert len(results) == 2


def test_agent_dependencies():
    """Verify agent dependency management"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("agent1", lambda: {"result": "1"})
    orchestrator.register_agent("agent2", lambda: {"result": "2"})

    orchestrator.set_dependency("agent2", "agent1")
    deps = orchestrator.get_dependencies("agent2")

    assert "agent1" in deps


def test_workflow_optimization():
    """Verify workflow optimization"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("agent1", lambda: {"result": "1"})
    orchestrator.register_agent("agent2", lambda: {"result": "2"})

    workflow = ["agent1", "agent2"]
    optimized = orchestrator.optimize_workflow(workflow)

    assert "optimized" in optimized


def test_error_handling():
    """Verify error handling in agent execution"""
    orchestrator = AIOrchestrator()

    orchestrator.register_agent(
        "failing_agent", lambda: (_ for _ in ()).throw(Exception("Failed"))
    )

    result = orchestrator.execute_agent("failing_agent")

    assert "error" in result


def test_agent_timeout():
    """Verify agent timeout handling"""
    orchestrator = AIOrchestrator(timeout=1)

    def slow_agent():
        import time

        time.sleep(10)
        return {"result": "done"}

    orchestrator.register_agent("slow_agent", slow_agent)

    result = orchestrator.execute_agent("slow_agent")

    assert "timeout" in result or "error" in result


def test_orchestrator_stats():
    """Verify getting orchestrator statistics"""
    orchestrator = AIOrchestrator()
    orchestrator.register_agent("agent1", lambda: {"result": "1"})
    orchestrator.execute_agent("agent1")

    stats = orchestrator.get_stats()

    assert "total_agents" in stats
    assert "total_executions" in stats
