# DynaBots Framework Family

**Multi-agent orchestration frameworks for the age of AI.**

This monorepo contains a family of orchestration frameworks, each with a different philosophy for coordinating AI agents:

| Package | Philosophy | Use Case |
|---------|------------|----------|
| **dynabots-core** | Shared primitives | Foundation for all frameworks |
| **dynabots** | DAG-based orchestration | Deterministic, parallel workflows |
| **dynabots-orc** | Brutalist hierarchy | Emergent leadership through competition |

## Quick Start

```bash
# Install core (required by all)
pip install dynabots-core[ollama]

# Install your preferred orchestration style
pip install dynabots  # DAG-based
pip install dynabots-orc  # Competition-based
```

## Philosophy

### DynaBots (DAG-based)

Pre-plan workflows as Directed Acyclic Graphs. Tasks execute in parallel waves. Predictable, auditable, deterministic.

```python
from dynabots import DynaBots

bots = DynaBots.create(
    agents={"DataAgent": data_agent, "ReportAgent": report_agent},
    llm=llm,
)

result = await bots.run("Fetch Q4 data and generate report")
# → Intent classification → Task decomposition → DAG execution
```

### Orc!! (Brutalist Hierarchy)

No appointed leaders. Leadership is earned through competition. The strongest agent leads until successfully challenged.

```python
from dynabots_orc import Arena, LLMJudge

arena = Arena(
    agents=[DataAgent(), ReportAgent(), AnalyticsAgent()],
    judge=LLMJudge(llm),
)

result = await arena.process("Analyze sales data")
# → Warlord executes OR challenger challenges → Trial → Succession
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                          │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ DynaBots │    │   Orc!!  │    │ [Future] │
    │   DAG    │    │  Arena   │    │  Hive?   │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │   dynabots-core     │
              │  Protocols & Types  │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ Ollama  │    │  OpenAI  │    │Anthropic │
    │ (Local) │    │  (API)   │    │  (API)   │
    └─────────┘    └──────────┘    └──────────┘
```

## Core Primitives

All frameworks share these building blocks:

### Agent Protocol

```python
from dynabots_core import Agent, TaskResult

class MyAgent:
    @property
    def name(self) -> str:
        return "MyAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["search", "analyze"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        result = await self.do_work(task)
        return TaskResult.success(task_id=context["task_id"], data=result)
```

### LLM Provider Protocol

```python
from dynabots_core.providers import OllamaProvider

# Local LLM
llm = OllamaProvider(model="qwen2.5:72b")

# Or OpenAI
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider
llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")
```

### TaskResult

```python
from dynabots_core import TaskResult

# Success
result = TaskResult.success(task_id="t1", data={"count": 42})

# No action needed (skip downstream)
result = TaskResult.no_action_needed(task_id="t1", reason="Already up to date")

# Failure
result = TaskResult.failure(task_id="t1", error="Connection failed")
```

## Comparison

| Feature | DynaBots | Orc!! |
|---------|----------|-------|
| **Leadership** | Central orchestrator | Emergent through competition |
| **Task Planning** | Pre-decomposed DAG | Dynamic, on-demand |
| **Parallelism** | Wave-based | Trial-based |
| **Predictability** | High | Medium |
| **Self-optimization** | No | Yes (best agent rises) |
| **Overhead** | Low | Higher (trials cost extra) |
| **Best for** | Known workflows | Competitive scenarios |

## Development

```bash
# Clone the repo
git clone https://github.com/Lumi-node/Dynabots
cd dynabots-framework/packages

# Install in development mode
pip install -e core[dev]
pip install -e orc[dev]

# Run tests
pytest core/tests
pytest orc/tests
```

## License

MIT
