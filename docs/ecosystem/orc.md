# ORC: Competitive Orchestration

Agents compete for leadership through trials. The best agent wins and becomes the Warlord until challenged.

---

## Overview

ORC implements **brutalist hierarchy**—a competitive orchestration philosophy where agents earn leadership through performance.

- **Agents compete**: Multiple agents process the same task
- **Judges evaluate**: Determine which agent did better
- **Succession**: Winner becomes the leader (Warlord)
- **Reputation**: Scores track agent performance over time
- **Domain-specific**: Different agents can lead different domains

---

## Installation

```bash
pip install dynabots-orc
```

Or install with core:

```bash
pip install dynabots-core dynabots-orc
```

---

## Quick Example

```python
import asyncio
from dynabots_orc import Arena, LLMJudge
from dynabots_core import TaskResult
from dynabots_core.providers import OllamaProvider

# Define competing agents
class DataAgent:
    @property
    def name(self) -> str:
        return "DataAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["fetch_data", "query"]

    @property
    def domains(self) -> list[str]:
        return ["data", "analytics"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        # Simulate data fetching
        return TaskResult.success(
            task_id=context["task_id"],
            data={"source": "database", "records": 42}
        )

    async def health_check(self) -> bool:
        return True

class AnalyticsAgent:
    @property
    def name(self) -> str:
        return "AnalyticsAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["analyze", "visualize"]

    @property
    def domains(self) -> list[str]:
        return ["analytics", "reporting"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        # Simulate analysis
        return TaskResult.success(
            task_id=context["task_id"],
            data={"insights": ["trend_up", "anomaly_detected"]}
        )

    async def health_check(self) -> bool:
        return True

async def main():
    # Create LLM judge
    llm = OllamaProvider(model="qwen2.5:7b")
    judge = LLMJudge(llm)

    # Create arena
    arena = Arena(
        agents=[DataAgent(), AnalyticsAgent()],
        judge=judge,
        on_challenge=lambda old, challenger, domain: print(
            f"Challenge: {challenger} vs {old} for {domain}"
        ),
        on_succession=lambda old, new, domain: print(
            f"Succession: {new} defeats {old} for {domain}"
        ),
    )

    # Process tasks
    result = await arena.process(
        "Analyze Q4 sales data",
        domain="analytics"
    )

    print(f"Winner: {result.winner}")
    print(f"Challenged: {result.was_challenged}")

asyncio.run(main())
```

---

## Core Concepts

### Arena

Manages competition between agents:

```python
from dynabots_orc import Arena

arena = Arena(
    agents=[agent1, agent2, agent3],
    judge=judge,
    on_challenge=challenge_handler,
    on_succession=succession_handler,
)

result = await arena.process("task description", domain="analytics")
```

### Warlord

The current leader for a domain:

```python
# Get current leader
warlord = arena.get_warlord("analytics")
print(f"Current leader: {warlord}")

# All warlords
leaders = arena.get_warlords()
# {"data": "DataAgent", "analytics": "AnalyticsAgent", ...}
```

### Trial

Head-to-head execution judged by a Judge:

```python
# Trials happen automatically when arena processes tasks
# But you can access the history
trials = arena.get_trial_history()

for trial in trials:
    print(f"{trial.domain}: {trial.winner} won")
```

### Reputation

Scores track agent performance:

```python
# Get an agent's reputation
score = arena.get_reputation("DataAgent", "data")
print(f"DataAgent's data score: {score}")

# Leaderboard
leaderboard = arena.get_leaderboard("data", limit=10)
for entry in leaderboard:
    print(f"{entry['agent']}: {entry['wins']} wins, rep {entry['reputation']:.2f}")
```

---

## Judges

Use any Judge implementation:

### LLM Judge

Use an LLM to evaluate submissions:

```python
from dynabots_orc import LLMJudge
from dynabots_core.providers import OllamaProvider

llm = OllamaProvider(model="qwen2.5:7b")
judge = LLMJudge(llm)

arena = Arena(agents=[...], judge=judge)
```

### Metrics Judge

Score by metrics (latency, cost, accuracy):

```python
from dynabots_orc import MetricsJudge

judge = MetricsJudge()
arena = Arena(agents=[...], judge=judge)
```

### Consensus Judge

Multiple judges vote:

```python
from dynabots_orc import ConsensusJudge

judges = [LLMJudge(llm1), MetricsJudge()]
judge = ConsensusJudge(judges)

arena = Arena(agents=[...], judge=judge)
```

---

## Challenge Strategies

Control when agents challenge the current leader:

### AlwaysChallenge

Challenge the leader every time:

```python
from dynabots_orc import AlwaysChallenge

agent.challenge_strategy = AlwaysChallenge()
```

### ReputationBased

Challenge if reputation is close:

```python
from dynabots_orc import ReputationBased

agent.challenge_strategy = ReputationBased(threshold=0.05)
# Challenge if rep differs by 5%
```

### Cooldown

Wait before challenging again:

```python
from dynabots_orc import Cooldown

agent.challenge_strategy = Cooldown(trials=5)
# Don't challenge for 5 trials
```

### Specialist

Challenge only in your domain:

```python
from dynabots_orc import Specialist

agent.challenge_strategy = Specialist()
```

---

## Storage (Optional)

Persist executions and reputation:

```python
from dynabots_orc import Arena

arena = Arena(
    agents=[...],
    judge=judge,
    execution_store=postgres_store,      # Save trials
    audit_store=blob_store,              # Audit logs
    reputation_store=postgres_reputation, # Track scores
)
```

All optional. Arena works without storage.

---

## Callbacks

Respond to events:

```python
def on_challenge(warlord: str, challenger: str, domain: str):
    print(f"{challenger} challenges {warlord} for {domain}")

def on_succession(old_warlord: str, new_warlord: str, domain: str):
    print(f"{new_warlord} defeats {old_warlord}")

def on_trial(result):
    print(f"Trial completed: {result.winner}")

arena = Arena(
    agents=[...],
    judge=judge,
    on_challenge=on_challenge,
    on_succession=on_succession,
    on_trial=on_trial,
)
```

---

## Domain Routing

Agents in different domains don't compete:

```python
# Agents
data_agent = DataAgent()        # domains: ["data", "analytics"]
report_agent = ReportAgent()    # domains: ["reporting"]

arena = Arena(agents=[data_agent, report_agent], judge=judge)

# These run separate trials (don't compete)
await arena.process("Fetch data", domain="data")
await arena.process("Generate report", domain="reporting")

# These compete (same domain)
await arena.process("Analyze sales", domain="analytics")
# Both data_agent and report_agent can handle "analytics"
# They compete via trial
```

---

## Advanced Usage

### Custom Result Handling

```python
result = await arena.process("task", domain="analytics")

print(result.winner)           # Winning agent
print(result.was_challenged)   # Was there a trial?
print(result.verdict)          # Judge's verdict
print(result.submissions)      # All submissions (if available)
```

### Monitor Progress

```python
# Check current warlords
for domain, warlord in arena.get_warlords().items():
    print(f"{domain}: {warlord}")

# Leaderboard by domain
for domain in ["data", "analytics", "reporting"]:
    top = arena.get_leaderboard(domain, limit=3)
    print(f"\n{domain.upper()}:")
    for entry in top:
        print(f"  {entry['agent']}: {entry['reputation']:.2f}")
```

### Trial History Analysis

```python
# Get all trials
trials = arena.get_trial_history()

# Filter by domain
analytics_trials = [t for t in trials if t.domain == "analytics"]

# Analyze patterns
for trial in analytics_trials:
    print(f"Trial in {trial.domain}: {trial.winner} won")
```

---

## Real-World Example

```python
import asyncio
from dynabots_orc import Arena, LLMJudge, ReputationBased
from dynabots_core import TaskResult
from dynabots_core.providers import OllamaProvider

class WebSearchAgent:
    challenge_strategy = ReputationBased(threshold=0.1)

    @property
    def name(self) -> str:
        return "WebSearchAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["search_web"]

    @property
    def domains(self) -> list[str]:
        return ["search", "information"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        # Real web search would go here
        return TaskResult.success(
            task_id=context["task_id"],
            data={"results": [{"title": "...", "url": "..."}]}
        )

    async def health_check(self) -> bool:
        return True

class LocalKBAgent:
    challenge_strategy = ReputationBased(threshold=0.05)

    @property
    def name(self) -> str:
        return "LocalKBAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["search_kb"]

    @property
    def domains(self) -> list[str]:
        return ["search", "information"]

    async def process_task(self, task: str, context: dict) -> TaskResult:
        # Search local knowledge base
        return TaskResult.success(
            task_id=context["task_id"],
            data={"results": [{"doc": "...", "excerpt": "..."}]}
        )

    async def health_check(self) -> bool:
        return True

async def main():
    llm = OllamaProvider(model="qwen2.5:7b")
    judge = LLMJudge(llm)

    arena = Arena(
        agents=[WebSearchAgent(), LocalKBAgent()],
        judge=judge,
    )

    # Simulate search queries
    queries = [
        "What is Python?",
        "How does OAuth work?",
        "Latest AI news",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = await arena.process(query, domain="search")
        print(f"Winner: {result.winner}")

    # Final standings
    print("\nFinal Standings:")
    leaderboard = arena.get_leaderboard("search")
    for agent in leaderboard:
        print(f"  {agent['agent']}: {agent['wins']} wins")

asyncio.run(main())
```

---

## See Also

- [ORC Repository](https://github.com/Lumi-node/ORC)
- [Agent Protocol](../protocols/agent.md)
- [Judge Protocol](../protocols/judge.md)
- [Roadmap](roadmap.md)
