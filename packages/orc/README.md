# Orc!! - Brutalist Hierarchy Orchestration

**No appointed leaders. Leadership is earned and contested.**

Orc!! is a multi-agent orchestration framework where agents compete for leadership through trials. The strongest agent leads until successfully challenged.

## Philosophy

In traditional orchestration, a central coordinator assigns tasks. In Orc!!, leadership emerges through competition:

- **Warlord**: The current leader for a domain - routes tasks and makes decisions
- **Challenge**: Any agent can challenge the Warlord for leadership
- **Trial**: Both agents attempt the same task - a Judge determines the winner
- **Succession**: The winner becomes (or remains) Warlord
- **Decay**: Leadership decays without successful defenses

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORC!! ARENA                              │
│                                                                  │
│    ┌─────────┐     challenges      ┌─────────┐                  │
│    │ Agent A │ ─────────────────► │ Agent B │                   │
│    │(Contender)                    │ (WARLORD)│                  │
│    └─────────┘                     └─────────┘                  │
│         │                               │                        │
│         │         TRIAL BY TASK         │                        │
│         │    ┌─────────────────────┐   │                        │
│         └───►│  Same task, both    │◄──┘                        │
│              │  attempt solution   │                             │
│              └──────────┬──────────┘                             │
│                         │                                        │
│                         ▼                                        │
│              ┌─────────────────────┐                             │
│              │       JUDGE         │                             │
│              │  Evaluates quality  │                             │
│              └──────────┬──────────┘                             │
│                         │                                        │
│              Winner becomes/stays WARLORD                        │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install dynabots-orc
```

## Quick Start

```python
import asyncio
from dynabots_orc import Arena, LLMJudge
from dynabots_core import Agent, TaskResult
from dynabots_core.providers import OllamaProvider

# Define your agents
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
        # Your implementation
        return TaskResult.success(task_id=context["task_id"], data="result")

class ReportAgent:
    @property
    def name(self) -> str:
        return "ReportAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["generate_report", "summarize"]

    @property
    def domains(self) -> list[str]:
        return ["reports", "data"]  # Overlaps with DataAgent!

    async def process_task(self, task: str, context: dict) -> TaskResult:
        return TaskResult.success(task_id=context["task_id"], data="report")


async def main():
    # Create arena with agents
    llm = OllamaProvider(model="qwen2.5:72b")
    judge = LLMJudge(llm)

    arena = Arena(
        agents=[DataAgent(), ReportAgent()],
        judge=judge,
        config=ArenaConfig(challenge_probability=0.3),
    )

    # Process a task - may trigger a trial!
    result = await arena.process("Analyze Q4 sales data")
    print(f"Winner: {result.winner}")
    print(f"Result: {result.data}")


asyncio.run(main())
```

## Core Concepts

### Arena

The Arena is where agents compete. It:
- Tracks the current Warlord for each domain
- Determines when challenges occur
- Executes trials between contenders
- Updates leadership based on outcomes

```python
arena = Arena(
    agents=[agent1, agent2, agent3],
    judge=my_judge,
    config=ArenaConfig(
        challenge_probability=0.3,    # How often to allow challenges
        leadership_decay_rate=0.01,   # Leadership decay rate
        min_trials_for_leadership=3,  # Minimum wins to become Warlord
    )
)
```

### Judges

Judges evaluate trial outcomes. Built-in options:

```python
from dynabots_orc.judges import LLMJudge, MetricsJudge, ConsensusJudge

# LLM-based evaluation
judge = LLMJudge(llm, criteria=["accuracy", "completeness", "efficiency"])

# Metrics-based evaluation
judge = MetricsJudge(
    weights={"accuracy": 0.5, "latency": 0.3, "cost": 0.2}
)

# Multiple judges vote
judge = ConsensusJudge([judge1, judge2, judge3])
```

### Challenge Strategies

Agents can use different strategies for when to challenge:

```python
from dynabots_orc.strategies import (
    AlwaysChallenge,        # Challenge whenever domains overlap
    ReputationBased,        # Challenge if my reputation is higher
    CooldownStrategy,       # Wait after losses before challenging again
    SpecialistStrategy,     # Only challenge in my specialty domain
)

# Attach strategy to agent
agent.challenge_strategy = ReputationBased(threshold=0.1)
```

### Reputation System

Agents build reputation through successful trials:

```python
# Get agent reputation
rep = arena.get_reputation("DataAgent", domain="data")

# Get leaderboard
leaders = arena.get_leaderboard(domain="data", limit=5)
```

## Why Orc!!?

| Traditional Orchestration | Orc!! |
|--------------------------|-------|
| Central coordinator decides | Leadership emerges from competition |
| Static role assignment | Dynamic, earned leadership |
| Single point of failure | Resilient - any agent can lead |
| No quality pressure | Continuous improvement through trials |

### Use Cases

- **Self-optimizing systems**: Best agent for each domain naturally rises
- **A/B testing agents**: Compare agent implementations head-to-head
- **Adversarial robustness**: Agents must prove competence
- **Research**: Study emergent hierarchies in multi-agent systems

## Advanced Usage

### Custom Trial Logic

```python
class MyArena(Arena):
    async def should_challenge(self, task: str, domain: str) -> bool:
        # Custom challenge logic
        if self._is_critical_task(task):
            return False  # No challenges for critical tasks
        return await super().should_challenge(task, domain)

    async def execute_trial(self, task, warlord, challenger):
        # Custom trial execution
        # Maybe run multiple rounds?
        results = []
        for _ in range(3):
            result = await super().execute_trial(task, warlord, challenger)
            results.append(result)
        return self._aggregate_results(results)
```

### Persistence

```python
from dynabots_orc import Arena
from dynabots_orc.storage import PostgresReputationStore

store = PostgresReputationStore(pool)
arena = Arena(
    agents=[...],
    judge=judge,
    reputation_store=store,  # Persist reputation across restarts
)
```

### Hooks

```python
arena = Arena(
    agents=[...],
    judge=judge,
    on_challenge=lambda w, c, d: print(f"{c} challenges {w} for {d}!"),
    on_succession=lambda old, new, d: print(f"{new} defeats {old}!"),
    on_trial_complete=lambda v: log_trial(v),
)
```

## Part of the DynaBots Family

| Package | Description |
|---------|-------------|
| `dynabots-core` | Shared primitives |
| `dynabots` | DAG-based orchestration |
| `dynabots-orc` | Challenge-based hierarchy (this package) |

## License

MIT
