# Agent Protocol

The core abstraction for agents in DynaBots. An agent processes tasks and returns results.

---

## Protocol Definition

::: dynabots_core.protocols.agent.Agent

---

## Simple Implementation

```python
from dynabots_core import Agent, TaskResult
from typing import Any, Dict, List

class SimpleAgent:
    """A minimal agent implementation."""

    @property
    def name(self) -> str:
        return "SimpleAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["greet", "answer"]

    async def process_task(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> TaskResult:
        """Execute a task."""
        if "hello" in task_description.lower():
            return TaskResult.success(
                task_id=context.get("task_id", "unknown"),
                data={"message": "Hello!"}
            )
        return TaskResult.failure(
            task_id=context.get("task_id", "unknown"),
            error="Unknown task"
        )

    async def health_check(self) -> bool:
        return True
```

---

## Advanced Implementation

With LLM-powered task understanding:

```python
import asyncio
from typing import Any, Dict, List
from dynabots_core import Agent, TaskResult, LLMMessage
from dynabots_core.providers import OllamaProvider

class LLMAgent:
    """Agent that uses LLM for smart task understanding."""

    def __init__(self, llm=None):
        self.llm = llm or OllamaProvider(model="qwen2.5:7b")
        self._tools = [
            self._search_knowledge_base,
            self._compute_calculation,
            self._generate_summary,
        ]

    @property
    def name(self) -> str:
        return "LLMAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["search", "compute", "summarize"]

    @property
    def domains(self) -> List[str]:
        return ["information", "analytics"]

    async def process_task(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> TaskResult:
        """Use LLM to understand and execute task."""
        task_id = context.get("task_id", "unknown")

        # Build prompt with available tools
        tools_info = "\n".join([
            f"- {tool.__name__}: {tool.__doc__}"
            for tool in self._tools
        ])

        prompt = f"""You are a helpful assistant.

Available tools:
{tools_info}

User request: {task_description}

Determine which tool(s) to use and execute them."""

        try:
            response = await self.llm.complete([
                LLMMessage(role="user", content=prompt)
            ])

            return TaskResult.success(
                task_id=task_id,
                data={"response": response.content}
            )
        except Exception as e:
            return TaskResult.failure(
                task_id=task_id,
                error=str(e)
            )

    async def health_check(self) -> bool:
        """Check if LLM is accessible."""
        try:
            response = await self.llm.complete([
                LLMMessage(role="user", content="ping")
            ])
            return bool(response.content)
        except Exception:
            return False

    async def _search_knowledge_base(self, query: str) -> str:
        """Search the knowledge base."""
        # Simulate search
        return f"Results for '{query}'"

    async def _compute_calculation(self, expr: str) -> str:
        """Compute a mathematical expression."""
        try:
            return str(eval(expr))
        except Exception as e:
            return f"Error: {e}"

    async def _generate_summary(self, text: str) -> str:
        """Generate a summary of text."""
        words = text.split()[:10]
        return " ".join(words) + "..."
```

---

## Domains and Capabilities

Use these to enable intelligent routing.

### Capabilities

List specific actions your agent can perform:

```python
@property
def capabilities(self) -> List[str]:
    return [
        "fetch_data",
        "query_database",
        "transform_data",
        "export_csv",
    ]
```

Used by orchestration frameworks to route tasks to capable agents.

### Domains

List topic areas your agent covers:

```python
@property
def domains(self) -> List[str]:
    return [
        "data",        # General data domain
        "analytics",   # Analytics focus
        "etl",         # Extract-transform-load
    ]
```

Used for smart routing and competition (agents compete within domains).

### Overlapping Domains

Multiple agents can cover the same domain. Orchestration frameworks (like ORC) use judges to determine which agent wins.

```python
# DataAgent
domains = ["data", "analytics"]

# AnalyticsAgent (also handles analytics!)
domains = ["analytics", "reporting"]

# Both cover "analytics" → they compete
```

---

## Task Context

The `context` dict passed to `process_task()` contains execution metadata:

```python
async def process_task(self, task: str, context: Dict[str, Any]) -> TaskResult:
    task_id = context["task_id"]
    workflow_id = context.get("workflow_id")
    parent_results = context.get("parent_results", [])
    user_context = context.get("user_context")

    # Use context in your task execution
    ...
```

Standard fields:

- `task_id`: Unique task identifier
- `workflow_id`: Parent workflow (optional)
- `parent_results`: Results from upstream tasks (optional)
- `user_context`: User metadata (email, etc.) (optional)

---

## Health Checks

The `health_check()` method enables liveness detection.

```python
async def health_check(self) -> bool:
    """Is this agent ready?"""
    try:
        # Check database connection
        await self.db.ping()
        # Check LLM connection
        await self.llm.complete([...])
        return True
    except Exception:
        return False
```

Orchestration frameworks periodically call `health_check()` to detect faulty agents.

---

## Type Checking

DynaBots protocols are `runtime_checkable`. Use `isinstance()` to validate:

```python
from dynabots_core import Agent

def use_agent(obj):
    if not isinstance(obj, Agent):
        raise TypeError(f"{obj} does not implement Agent protocol")
    # Safe to use as Agent
```

---

## Execution Modes

### Smart Mode (Recommended)

Your agent uses its own LLM to understand tasks:

```python
async def process_task(self, task: str, context: dict) -> TaskResult:
    # Parse task with LLM
    plan = await self.llm.understand(task)
    # Execute plan
    result = await self.execute_plan(plan)
    return TaskResult.success(task_id=context["task_id"], data=result)
```

Pros:
- Flexible task understanding
- Use any tools
- Better for complex tasks

### Legacy Mode (Optional)

Implement `execute_capability()` for direct routing:

```python
from typing import Any, Dict, List, Protocol, runtime_checkable

@runtime_checkable
class LegacyAgent(Protocol):
    async def execute_capability(
        self,
        capability: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
    ) -> "TaskResult":
        """Execute a specific capability directly."""
        ...
```

Pros:
- Predictable, direct routing
- Good for well-defined operations
- No LLM overhead

---

## Best Practices

1. **Stateless agents**: Agents should be stateless. Store data in dedicated services.
2. **Health checks**: Always implement `health_check()`. Return fast.
3. **Domains**: Be specific with domains. Overlapping domains enable competition.
4. **Error handling**: Return `TaskResult.failure()` with clear error messages.
5. **Metadata**: Use `TaskResult.metadata` to attach domain-specific data.

---

## See Also

- [Core Concepts: Agent](../getting-started/concepts.md#agent)
- [TaskResult](../value-objects/task-result.md)
- [LLM Providers](../providers/overview.md)
- [Quick Start](../getting-started/quick-start.md)
