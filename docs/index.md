# DynaBots

**Multi-Agent Orchestration for Python**

A protocol-first foundation for building, evaluating, and deploying AI agent systems.

---

## Core Features

### Protocol-First Design

No inheritance required. DynaBots uses Python's `Protocol` for structural subtyping. Implement the right methods and your class works—no base classes, no coupling, no framework lock-in.

### Any LLM

Swap providers without changing your agent code. Unified interface for Ollama (local), OpenAI, Anthropic, or any LLM service.

### Extensible Ecosystem

Base package (`dynabots-core`) provides protocols and primitives. Orchestration packages (`ORC`, future frameworks) layer on top. All independently installable, all share the same foundation.

---

## Quick Install

```bash
pip install dynabots-core
```

Optional provider extras:

```bash
# Use specific providers
pip install dynabots-core[openai]
pip install dynabots-core[anthropic]
pip install dynabots-core[ollama]

# Or install all providers
pip install dynabots-core[all]
```

---

## Quick Example

### 1. Define an Agent

Implement the `Agent` protocol. That's it—no base class required.

```python
from dynabots_core import Agent, TaskResult

class DataAgent:
    @property
    def name(self) -> str:
        return "DataAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["fetch_data", "analyze"]

    @property
    def domains(self) -> list[str]:
        return ["data", "analytics"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        # Use your agent's LLM to pick tools
        result = await self.do_work(task)
        return TaskResult.success(
            task_id=context["task_id"],
            data=result
        )

    async def health_check(self) -> bool:
        return True
```

### 2. Use an LLM Provider

```python
from dynabots_core.providers import OllamaProvider

# Local model via Ollama
llm = OllamaProvider(model="qwen2.5:7b")

# Or OpenAI
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider
llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

# Or Anthropic
from anthropic import AsyncAnthropic
from dynabots_core.providers import AnthropicProvider
llm = AnthropicProvider(AsyncAnthropic(), model="claude-3-5-sonnet-20241022")
```

### 3. Run Your Agent

```python
import asyncio

async def main():
    agent = DataAgent()
    result = await agent.process_task(
        "Analyze Q4 sales data",
        {"task_id": "task_001"}
    )
    print(result.data)

asyncio.run(main())
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Your Application               │
└─────────────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │   ORC    │ │ [Future] │ │ [Future] │
   │  Arena   │ │   DAG    │ │  Swarm   │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        └─────────────┼────────────┘
                      ▼
           ┌─────────────────────┐
           │  dynabots-core      │
           │  Protocols & Types  │
           └──────────┬──────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ Ollama  │  │  OpenAI  │  │Anthropic │
   └─────────┘  └──────────┘  └──────────┘
```

---

## What's Included

### dynabots-core

Zero-dependency protocol foundation.

- **Agent**: Process natural language tasks, health checks
- **LLMProvider**: Unified interface for any LLM service
- **Judge**: Evaluate and compare agent submissions
- **Tool**: JSON-schema tool definitions for function calling
- **TaskResult**: Rich outcome semantics (success/failure/skip/partial)
- **Providers**: OpenAI, Anthropic, Ollama adapters

### dynabots-orc

Competitive orchestration—agents earn leadership through trials.

```bash
pip install dynabots-orc
```

Agents compete for domain leadership. The best performer becomes the Warlord until challenged.

```python
from dynabots_orc import Arena, LLMJudge

arena = Arena(
    agents=[DataAgent(), AnalyticsAgent()],
    judge=LLMJudge(llm),
    on_succession=lambda old, new, domain: print(f"{new} defeats {old}!")
)

result = await arena.process("Analyze Q4 data")
print(f"Winner: {result.winner}")
```

---

## Documentation

- **[Getting Started](getting-started/installation.md)**: Installation and setup
- **[Quick Start](getting-started/quick-start.md)**: Your first agent in 5 minutes
- **[Core Concepts](getting-started/concepts.md)**: Protocols, TaskResult, and patterns
- **[Protocols](protocols/agent.md)**: Complete protocol reference
- **[Providers](providers/overview.md)**: LLM provider guide
- **[Value Objects](value-objects/task-result.md)**: TaskResult semantics
- **[Ecosystem](ecosystem/orc.md)**: ORC and future packages

---

## Key Principles

**Protocol-First**: Structural subtyping, no inheritance, maximum flexibility.

**Zero Dependencies**: dynabots-core has no external dependencies. Add only what you need.

**Unified Interfaces**: One way to talk to any LLM, any judge, any storage backend.

**Composable**: Protocols layer on top of each other. Mix and match.

**Extensible**: Implement a protocol, use it everywhere.

---

## Next Steps

1. [Install dynabots-core](getting-started/installation.md)
2. [Build your first agent](getting-started/quick-start.md)
3. [Learn the protocols](getting-started/concepts.md)
4. [Explore ORC orchestration](ecosystem/orc.md)

---

## License

Apache 2.0 — See [LICENSE](https://github.com/Lumi-node/Dynabots/blob/main/LICENSE) for details.

## Contributing

Contributions welcome. See [CONTRIBUTING.md](https://github.com/Lumi-node/Dynabots/blob/main/CONTRIBUTING.md) for guidelines.
