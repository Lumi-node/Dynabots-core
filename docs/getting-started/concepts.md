# Core Concepts

---

## Protocols vs Classes

DynaBots uses Python's `Protocol` for structural subtyping instead of base classes.

### What's a Protocol?

A Protocol defines a contract (a set of methods/properties) without imposing inheritance.

```python
# Traditional base class approach
class Agent(ABC):
    @abstractmethod
    def process_task(self, task: str) -> TaskResult:
        pass

# All agents must inherit
class MyAgent(Agent):  # Must inherit
    async def process_task(self, task: str) -> TaskResult:
        ...

# Protocol approach (DynaBots)
from typing import Protocol

class Agent(Protocol):
    async def process_task(self, task: str) -> TaskResult:
        ...

# Your class just needs these methods—no inheritance required
class MyAgent:  # No base class!
    async def process_task(self, task: str) -> TaskResult:
        ...

# It works anywhere an Agent is expected
agent: Agent = MyAgent()  # Type checking works
```

### Why Protocols?

**Maximum Flexibility**

- No coupling to framework code
- Your agents are plain classes
- Mix DynaBots with any other framework
- Protocol is just a type hint; it's not enforced at runtime unless you use `isinstance()` on a `@runtime_checkable` protocol

**Zero Inheritance Chain**

- Cleaner code
- No method resolution order (MRO) issues
- Easy to test (just instantiate your class)

**Composable**

- Implement multiple protocols
- Different modules can define their own protocols
- No version lock-in to framework base classes

---

## Agent

An Agent is the core abstraction. It processes tasks and returns results.

### The Agent Protocol

```python
from dynabots_core import Agent, TaskResult

class MyAgent:
    @property
    def name(self) -> str:
        """Unique identifier for this agent."""
        return "MyAgent"

    @property
    def capabilities(self) -> list[str]:
        """What this agent can do."""
        return ["search", "analyze", "report"]

    @property
    def domains(self) -> list[str]:
        """What domains this agent covers."""
        return ["data", "analytics"]

    async def process_task(
        self,
        task_description: str,
        context: dict,
    ) -> TaskResult:
        """Execute a task described in natural language."""
        # Use your LLM to understand the task
        # Pick the right tool
        # Execute and return result
        return TaskResult.success(
            task_id=context["task_id"],
            data={"result": "..."}
        )

    async def health_check(self) -> bool:
        """Is this agent ready to work?"""
        return True
```

### Properties

- `name`: Unique identifier. Used by orchestration frameworks.
- `capabilities`: List of capability names (e.g., "search", "analyze"). Used for routing.
- `domains`: Domain keywords (e.g., "data", "analytics"). Used for smart routing and competition.

### Methods

- `process_task(task_description, context)`: Execute a task in natural language. Return a `TaskResult`.
- `health_check()`: Liveness check. Return `True` if healthy.

### Execution Modes

**Smart Mode** (Recommended)

Your agent uses its own LLM to understand the task and pick tools.

```python
async def process_task(self, task: str, context: dict) -> TaskResult:
    # Use your agent's LLM
    plan = await self.llm.plan(task, self.tools)
    result = await self.execute_plan(plan)
    return TaskResult.success(task_id=context["task_id"], data=result)
```

**Legacy Mode** (Optional)

Implement `execute_capability()` for direct capability routing.

```python
async def execute_capability(
    self,
    capability: str,
    parameters: dict,
    context: dict,
) -> TaskResult:
    # Direct routing, bypass LLM
    if capability == "search":
        return await self._search(**parameters)
    ...
```

---

## LLMProvider

A unified interface for any LLM service.

### The Protocol

```python
from dynabots_core import LLMProvider, LLMMessage, LLMResponse

class MyLLMProvider:
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        """Send messages and get a response."""
        # Call your LLM service
        # Return LLMResponse
        ...
```

### Built-in Providers

DynaBots provides three providers:

- **OllamaProvider**: Local models (Llama, Qwen, Mixtral, etc.)
- **OpenAIProvider**: OpenAI and Azure OpenAI
- **AnthropicProvider**: Claude models

### Usage

```python
from dynabots_core.providers import OllamaProvider

llm = OllamaProvider(model="qwen2.5:7b")

response = await llm.complete([
    LLMMessage(role="system", content="You are helpful."),
    LLMMessage(role="user", content="Hello!"),
])

print(response.content)  # "Hi! How can I help?"
```

### Swapping Providers

Change your LLM without changing your agent code.

```python
# Start with Ollama
llm = OllamaProvider(model="qwen2.5:7b")

# Later, switch to OpenAI
from dynabots_core.providers import OpenAIProvider
from openai import AsyncOpenAI

llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

# Same agent code works with both
agent.llm = llm
```

---

## TaskResult

The outcome of a task execution. Rich semantics for workflow control.

### Outcomes

TaskResult can have one of five outcomes:

| Outcome | Meaning | should_continue |
|---------|---------|-----------------|
| `SUCCESS` | Task succeeded, return data | `True` |
| `FAILURE` | Task failed, return error | `False` |
| `NO_ACTION_NEEDED` | Nothing to do, skip downstream | `False` |
| `PARTIAL` | Partial success, some data | `True` |
| `SKIPPED` | Task was skipped | `False` |

### Creating Results

```python
from dynabots_core import TaskResult

# Success
return TaskResult.success(
    task_id="task_001",
    data={"records": 42}
)

# No action needed (skip downstream tasks)
return TaskResult.no_action_needed(
    task_id="task_002",
    reason="Already up to date"
)

# Failure
return TaskResult.failure(
    task_id="task_003",
    error="Connection timeout"
)

# Partial success
return TaskResult.partial(
    task_id="task_004",
    data={"records": 35},
    reason="Timeout after 30s, got partial results"
)

# Skipped
return TaskResult.skipped(
    task_id="task_005",
    reason="Condition not met"
)
```

### Conditional Execution

Use TaskResult to control workflow flow.

```python
# In orchestration logic
result = await agent.process_task(task, context)

if result.should_continue:
    # Run downstream tasks
    await run_next_task(result.data)
else:
    # Stop execution
    print(f"Skipping: {result.skip_reason}")
```

### Properties

```python
result = await agent.process_task(task, context)

# Check outcome
result.is_success          # True if SUCCESS
result.is_failure          # True if FAILURE
result.is_no_action_needed # True if NO_ACTION_NEEDED
result.is_skipped          # True if SKIPPED

# Conditional logic
result.is_actionable       # False for FAILURE, NO_ACTION_NEEDED, SKIPPED

# Data
result.data                # The returned data
result.error_message       # Error if FAILURE

# Metadata
result.task_id             # Task identifier
result.duration_ms         # Execution time in milliseconds
result.timestamp           # When result was created
result.metadata            # Custom metadata
```

---

## Judge

Evaluates and compares agent submissions. Used in competitive orchestration.

### The Protocol

```python
from dynabots_core import Judge, Verdict, Submission

class MyJudge:
    async def evaluate(
        self,
        task: str,
        submissions: list[Submission],
    ) -> Verdict:
        """Evaluate submissions and return a verdict."""
        # Compare submissions
        # Determine winner
        # Return Verdict
        ...
```

### What Judges Do

Compare multiple agents' outputs and pick a winner.

```python
submissions = [
    Submission(
        agent="Agent1",
        result=TaskResult.success(...),
        latency_ms=100,
        cost=0.01
    ),
    Submission(
        agent="Agent2",
        result=TaskResult.success(...),
        latency_ms=150,
        cost=0.02
    ),
]

verdict = await judge.evaluate("Do X", submissions)
print(verdict.winner)      # "Agent1"
print(verdict.reasoning)   # Why Agent1 won
print(verdict.scores)      # {"Agent1": 0.9, "Agent2": 0.7}
```

### Implementation Strategies

- **LLM-based**: Ask another model to judge quality
- **Metrics-based**: Score by latency, cost, accuracy
- **Consensus**: Multiple judges vote
- **Domain-specific**: Custom rules for your domain

---

## Tool

A callable action an agent can take. For function calling.

### The Protocol

```python
from dynabots_core import Tool

class SearchTool:
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Search the knowledge base"

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }

    async def execute(self, query: str, limit: int = 10) -> list:
        return await self.kb.search(query, limit)
```

### Parameters Schema

JSON Schema format. Enables:

- LLM understanding of what parameters to pass
- Validation of inputs
- Auto-generation of documentation

---

## Storage Protocols

Optional. DynaBots works without storage. Add it for persistence and optimization.

### ExecutionStore

History of completed executions.

```python
from dynabots_core import ExecutionStore

store = MyExecutionStore()
await store.save_workflow({"id": "wf_001", "status": "completed", ...})

history = await store.list_workflows(limit=50)
```

### AuditStore

Immutable audit logs for compliance.

```python
from dynabots_core import AuditStore

audit = MyAuditStore()
await audit.log_workflow("wf_001", {"action": "completed", ...})
```

### CacheStore

Pattern cache for O(1) routing.

```python
from dynabots_core import CacheStore

cache = MyCacheStore()
await cache.set("pattern_001", {"agent": "DataAgent", ...})

entry = await cache.get("pattern_001")
```

### ReputationStore

Agent reputation tracking (used by ORC).

```python
from dynabots_core import ReputationStore

reputation = MyReputationStore()
score = await reputation.get_reputation("DataAgent", "data")
await reputation.update_reputation("DataAgent", "data", +0.1)
```

---

## Summary

| Concept | Purpose | Configurable |
|---------|---------|--------------|
| **Agent** | Core abstraction for task execution | Implement the protocol |
| **LLMProvider** | Unified interface for any LLM | Swap anytime |
| **TaskResult** | Rich outcome semantics for workflows | Return appropriate outcome |
| **Judge** | Compare and score submissions | Your implementation |
| **Tool** | Callable action with schema | Define for your domain |
| **Storage** | Persistence and optimization | Optional, pluggable |

All are **protocols**, not base classes. Implement them however you want.
