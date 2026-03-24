# DynaBots

**A family of multi-agent orchestration frameworks for Python.**

DynaBots provides multiple orchestration philosophies for coordinating AI agents, each as an independent, installable package sharing a common protocol foundation.

## Packages

| Package | Install | Philosophy |
|---------|---------|------------|
| [**dynabots-core**](packages/core/) | `pip install dynabots-core` | Zero-dependency protocols, LLM providers, and shared primitives |
| [**dynabots-orc**](packages/orc/) | `pip install dynabots-orc` | Brutalist hierarchy — agents earn leadership through competition |

## Quick Start

```bash
pip install dynabots-core dynabots-orc
```

### Define an Agent

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
        result = await self.do_work(task)
        return TaskResult.success(task_id=context["task_id"], data=result)
```

### Run a Competitive Arena (ORC!!)

Agents compete for domain leadership. The best agent leads until challenged.

```python
import asyncio
from dynabots_orc import Arena, ArenaConfig, MetricsJudge

arena = Arena(
    agents=[DataAgent(), AnalyticsAgent(), ReportAgent()],
    judge=MetricsJudge(),
    config=ArenaConfig(challenge_probability=0.3),
    on_succession=lambda old, new, d: print(f"{new} defeats {old} for '{d}'!"),
)

result = await arena.process("Analyze Q4 sales data")
print(f"Winner: {result.winner}")
```

### Use Any LLM Provider

```python
from dynabots_core.providers import OllamaProvider, OpenAIProvider, AnthropicProvider

# Local (Ollama)
llm = OllamaProvider(model="qwen2.5:7b")

# OpenAI
from openai import AsyncOpenAI
llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

# Anthropic
from anthropic import AsyncAnthropic
llm = AnthropicProvider(AsyncAnthropic(), model="claude-sonnet-4-20250514")
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              Your Application               │
└─────────────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  ORC!!   │ │ [Future] │ │ [Future] │
   │  Arena   │ │  DAG     │ │  Swarm   │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        └─────────────┼────────────┘
                      ▼
           ┌─────────────────────┐
           │   dynabots-core     │
           │  Protocols & Types  │
           └──────────┬──────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ Ollama  │  │  OpenAI  │  │Anthropic │
   └─────────┘  └──────────┘  └──────────┘
```

## Core Concepts

### dynabots-core

Zero-dependency protocol foundation. Define agents, LLM providers, judges, and tools using Python protocols:

- **Agent** — `process_task(task, context) -> TaskResult`
- **LLMProvider** — Unified interface for OpenAI, Anthropic, Ollama
- **Judge** — `evaluate(task, submissions) -> Verdict`
- **Tool** — JSON-schema function definitions
- **TaskResult** — Immutable outcome with success/failure/skip semantics

### dynabots-orc (ORC!!)

Competitive orchestration where leadership is earned, not assigned:

- **Arena** — Manages competition between agents
- **Warlord** — Current leader for a domain
- **Trial** — Head-to-head task execution judged by a Judge
- **Succession** — Winner becomes the new Warlord
- **Reputation** — Scores track agent performance over time
- **Strategies** — AlwaysChallenge, ReputationBased, Cooldown, Specialist

## Project Structure

```
Dynabots/
├── packages/
│   ├── core/                    # dynabots-core (pip install dynabots-core)
│   │   ├── dynabots_core/
│   │   │   ├── protocols/       # Agent, LLM, Judge, Tool, Storage
│   │   │   ├── providers/       # OpenAI, Anthropic, Ollama
│   │   │   └── value_objects/   # TaskResult
│   │   └── tests/
│   ├── orc/                     # dynabots-orc (pip install dynabots-orc)
│   │   ├── dynabots_orc/
│   │   │   ├── arena/           # Arena, Trial
│   │   │   ├── judges/          # LLMJudge, MetricsJudge, ConsensusJudge
│   │   │   └── strategies/      # Challenge strategies
│   │   └── tests/
│   └── examples/                # Runnable examples
└── examples/
    └── enterprise-automation/   # 5-agent, 264-tool demo
```

## Development

```bash
git clone https://github.com/Lumi-node/Dynabots.git
cd Dynabots

# Install in development mode
pip install -e "packages/core[dev]"
pip install -e "packages/orc[dev]"

# Run tests
pytest packages/core/tests/ packages/orc/tests/ -v

# Run examples
python packages/examples/orc_arena_example.py
```

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
