"""
Simple Agent Example

Demonstrates how to create an agent using dynabots-core primitives.

Run with:
    python simple_agent_example.py
"""

import asyncio
from typing import Any, Dict, List

from dynabots_core import Agent, TaskResult, LLMMessage
from dynabots_core.providers import OllamaProvider


class SimpleSearchAgent:
    """
    A simple agent that can search and summarize.

    This demonstrates the Agent protocol from dynabots-core.
    """

    def __init__(self, llm=None):
        """Initialize with optional LLM for smart mode."""
        self.llm = llm
        self._database = {
            "Alice": {"role": "Engineer", "department": "R&D"},
            "Bob": {"role": "Manager", "department": "Sales"},
            "Charlie": {"role": "Designer", "department": "Product"},
        }

    @property
    def name(self) -> str:
        return "SimpleSearchAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["search_employees", "get_employee_details", "summarize"]

    @property
    def domains(self) -> List[str]:
        return ["employees", "hr", "search"]

    async def process_task(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> TaskResult:
        """
        Smart Mode: Process a task described in natural language.

        The agent decides how to accomplish the task.
        """
        task_id = context.get("task_id", "unknown")
        task_lower = task_description.lower()

        # Simple keyword-based routing (in production, use LLM)
        if "search" in task_lower or "find" in task_lower:
            # Extract name (simple heuristic)
            for name in self._database.keys():
                if name.lower() in task_lower:
                    return await self._search(name, task_id)
            return await self._list_all(task_id)

        elif "details" in task_lower or "info" in task_lower:
            for name in self._database.keys():
                if name.lower() in task_lower:
                    return await self._get_details(name, task_id)
            return TaskResult.failure(task_id, "No employee name found in request")

        elif "summarize" in task_lower or "summary" in task_lower:
            return await self._summarize(task_id)

        else:
            # If we have an LLM, use it to understand the task
            if self.llm:
                return await self._process_with_llm(task_description, context)
            return TaskResult.failure(task_id, f"Unknown task: {task_description}")

    async def _search(self, name: str, task_id: str) -> TaskResult:
        """Search for an employee."""
        if name in self._database:
            return TaskResult.success(
                task_id=task_id,
                data={"found": True, "name": name, **self._database[name]},
            )
        return TaskResult.no_action_needed(task_id, f"Employee '{name}' not found")

    async def _list_all(self, task_id: str) -> TaskResult:
        """List all employees."""
        return TaskResult.success(
            task_id=task_id,
            data={"employees": list(self._database.keys())},
        )

    async def _get_details(self, name: str, task_id: str) -> TaskResult:
        """Get employee details."""
        if name in self._database:
            return TaskResult.success(
                task_id=task_id,
                data={"name": name, **self._database[name]},
            )
        return TaskResult.failure(task_id, f"Employee '{name}' not found")

    async def _summarize(self, task_id: str) -> TaskResult:
        """Summarize the employee database."""
        by_dept = {}
        for name, info in self._database.items():
            dept = info["department"]
            by_dept.setdefault(dept, []).append(name)

        return TaskResult.success(
            task_id=task_id,
            data={
                "total_employees": len(self._database),
                "departments": by_dept,
            },
        )

    async def _process_with_llm(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> TaskResult:
        """Use LLM to understand and process the task."""
        task_id = context.get("task_id", "unknown")

        prompt = f"""You are an assistant helping with employee queries.

Available employees:
{self._database}

Task: {task_description}

Respond with the relevant information."""

        response = await self.llm.complete([
            LLMMessage(role="user", content=prompt),
        ])

        return TaskResult.success(task_id=task_id, data={"response": response.content})

    async def health_check(self) -> bool:
        """Check if agent is healthy."""
        return True


async def main():
    print("Simple Agent Example")
    print("=" * 50)

    # Try to use Ollama, fall back to no LLM
    try:
        llm = OllamaProvider(model="qwen2.5:7b")
        print("Using Ollama LLM for smart mode")
    except Exception as e:
        llm = None
        print(f"No LLM available ({e}), using keyword-based routing")

    agent = SimpleSearchAgent(llm=llm)

    # Test various tasks
    tasks = [
        "Search for Alice",
        "Get details for Bob",
        "Find Charlie's information",
        "Summarize the employee database",
        "List all employees",
        "What department is Alice in?",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n--- Task {i}: {task} ---")
        result = await agent.process_task(task, {"task_id": f"task_{i}"})
        print(f"Outcome: {result.outcome.value}")
        print(f"Data: {result.data}")


if __name__ == "__main__":
    asyncio.run(main())
