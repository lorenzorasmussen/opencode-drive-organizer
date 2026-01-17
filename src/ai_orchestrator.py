"""
AI Orchestrator for coordinating AI agents
"""

import time
import threading
from typing import Dict, List, Callable, Optional
from datetime import datetime


class AIOrchestrator:
    """
    AI Orchestrator for coordinating OpenCode agents

    Features:
    - Register agents
    - Execute agents
    - Workflow execution
    - Parallel execution
    - Dependency management
    - Workflow optimization
    - Error handling
    - Timeout handling
    - Statistics tracking
    """

    def __init__(self, timeout: int = 60):
        """
        Initialize AI orchestrator

        Args:
            timeout: Default timeout for agent execution in seconds
        """
        self.agents = {}
        self.dependencies = {}
        self.timeout = timeout
        self.stats = {
            "total_agents": 0,
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
        }

    def register_agent(self, name: str, agent_func: Callable):
        """
        Register an AI agent

        Args:
            name: Agent name
            agent_func: Agent function to execute
        """
        self.agents[name] = agent_func
        self.stats["total_agents"] += 1

    def execute_agent(self, name: str, **kwargs) -> Dict:
        """
        Execute a single agent

        Args:
            name: Agent name to execute
            **kwargs: Arguments to pass to agent

        Returns:
            Result dict with status, output, or error
        """
        if name not in self.agents:
            return {"status": "error", "error": f"Agent {name} not found"}

        self.stats["total_executions"] += 1

        try:
            # Execute with timeout
            result = self._execute_with_timeout(name, **kwargs)

            self.stats["successful_executions"] += 1

            return {
                "status": "success",
                "output": result,
                "executed_at": datetime.now().isoformat(),
            }
        except Exception as e:
            self.stats["failed_executions"] += 1
            return {
                "status": "error",
                "error": str(e),
                "executed_at": datetime.now().isoformat(),
            }

    def execute_workflow(self, workflow: List[str]) -> List[Dict]:
        """
        Execute a workflow of agents

        Args:
            workflow: List of agent names in execution order

        Returns:
            List of result dicts
        """
        results = []

        for agent_name in workflow:
            # Check dependencies
            deps = self.dependencies.get(agent_name, [])
            for dep in deps:
                if dep not in [r.get("agent") for r in results]:
                    results.append(
                        {
                            "agent": dep,
                            "status": "skipped",
                            "reason": "Dependency not met",
                        }
                    )

            # Execute agent
            result = self.execute_agent(agent_name)
            result["agent"] = agent_name
            results.append(result)

            # Stop if failed
            if result["status"] == "error":
                break

        return results

    def execute_parallel(self, agents: List[str]) -> List[Dict]:
        """
        Execute multiple agents in parallel

        Args:
            agents: List of agent names

        Returns:
            List of result dicts
        """
        results = [None] * len(agents)
        threads = []

        def execute_wrapper(idx, name):
            result = self.execute_agent(name)
            results[idx] = result

        # Create and start threads
        for i, agent_name in enumerate(agents):
            thread = threading.Thread(target=execute_wrapper, args=(i, agent_name))
            thread.start()
            threads.append(thread)

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=self.timeout)

        # Add agent names to results
        for i, result in enumerate(results):
            if result:
                result["agent"] = agents[i]

        return results

    def set_dependency(self, agent: str, dependency: str):
        """
        Set dependency for an agent

        Args:
            agent: Agent name
            dependency: Agent it depends on
        """
        if agent not in self.dependencies:
            self.dependencies[agent] = []

        if dependency not in self.dependencies[agent]:
            self.dependencies[agent].append(dependency)

    def get_dependencies(self, agent: str) -> List[str]:
        """
        Get dependencies for an agent

        Args:
            agent: Agent name

        Returns:
            List of dependency names
        """
        return self.dependencies.get(agent, [])

    def optimize_workflow(self, workflow: List[str]) -> Dict:
        """
        Optimize workflow for parallel execution

        Args:
            workflow: List of agent names

        Returns:
            Dict with optimized workflow
        """
        # Find agents that can run in parallel (no dependencies)
        parallel_groups = []
        current_group = []

        for agent in workflow:
            deps = self.get_dependencies(agent)
            # Check if all dependencies are in previous groups
            if not deps or all(
                d in [a for group in parallel_groups for a in group] for d in deps
            ):
                current_group.append(agent)
            else:
                if current_group:
                    parallel_groups.append(current_group)
                    current_group = []
                current_group.append(agent)

        if current_group:
            parallel_groups.append(current_group)

        return {
            "original": workflow,
            "optimized": parallel_groups,
            "parallelization_factor": len(workflow) / max(len(parallel_groups), 1),
        }

    def _execute_with_timeout(self, name: str, **kwargs):
        """Execute agent with timeout"""

        def target():
            return self.agents[name](**kwargs)

        result_wrapper = [None]
        exception_wrapper = [None]

        def wrapper():
            try:
                result_wrapper[0] = target()
            except Exception as e:
                exception_wrapper[0] = e

        thread = threading.Thread(target=wrapper)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            # Thread still running after timeout
            thread.join(timeout=1)
            if thread.is_alive():
                raise TimeoutError(f"Agent {name} timed out after {self.timeout}s")

        if exception_wrapper[0]:
            raise exception_wrapper[0]

        return result_wrapper[0]

    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return self.stats.copy()
