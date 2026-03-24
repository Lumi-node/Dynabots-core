# dynabots-core

Core primitives for the DynaBots orchestration framework family.

## Overview

`dynabots-core` provides the foundational building blocks shared across all DynaBots orchestration frameworks:

- **Protocols**: `Agent`, `LLMProvider`, `Judge`, `Tool` - interfaces that define contracts
- **Value Objects**: `TaskResult`, `LLMMessage`, `LLMResponse` - immutable data structures
- **Providers**: Ready-to-use LLM adapters for OpenAI, Ollama, Anthropic

## Installation

```bash
# Core only (bring your own LLM client)
pip install dynabots-core

# With OpenAI support
pip install dynabots-core[openai]

# With Ollama (local LLMs)
pip install dynabots-core[ollama]

# With all providers
pip install dynabots-core[all]
```

## Quick Start

### Define an Agent

```python
from dynabots_core import Agent, TaskResult

class MyAgent:
    @property
    def name(self) -> str:
        return "MyAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["search", "summarize"]

    async def process_task(self, task_description: str, context: dict) -> TaskResult:
        # Your agent logic here
        result = await self._do_work(task_description)
        return TaskResult.success(
            task_id=context["task_id"],
            data=result
        )
```

### Use an LLM Provider

```python
from dynabots_core.providers import OllamaProvider

# Local LLM via Ollama
llm = OllamaProvider(model="qwen2.5:72b")

response = await llm.complete([
    LLMMessage(role="system", content="You are a helpful assistant."),
    LLMMessage(role="user", content="Hello!")
])
print(response.content)
```

### Create a Judge (for Orc!!)

```python
from dynabots_core import Judge, Verdict

class LLMJudge:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def evaluate(self, task: str, submissions: list[dict]) -> Verdict:
        # Compare submissions and pick a winner
        prompt = f"Task: {task}\n\nSubmission A: {submissions[0]}\nSubmission B: {submissions[1]}\n\nWhich is better?"
        response = await self.llm.complete([LLMMessage(role="user", content=prompt)])
        return Verdict(winner=..., reasoning=response.content)
```

## Framework Family

This package is part of the DynaBots framework family:

| Package | Description |
|---------|-------------|
| `dynabots-core` | Shared primitives (this package) |
| `dynabots` | DAG-based orchestration with parallel waves |
| `orc` | Challenge-based hierarchy with contested leadership |

## Protocols

### Agent

```python
class Agent(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> list[str]: ...

    async def process_task(self, task_description: str, context: dict) -> TaskResult: ...
```

### LLMProvider

```python
class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> LLMResponse: ...
```

### Judge

```python
class Judge(Protocol):
    async def evaluate(self, task: str, submissions: list[dict]) -> Verdict: ...
```

### Tool

```python
class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def parameters_schema(self) -> dict: ...

    async def execute(self, **kwargs) -> Any: ...
```

## License

MIT
