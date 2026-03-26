# Roadmap

Future orchestration packages built on the `dynabots-core` foundation.

---

## Vision

DynaBots is a family of orchestration philosophies. Each package explores a different approach to coordinating AI agents:

- **ORC** (Current): Competitive hierarchy — agents earn leadership through trials
- **SAO** (Planned): Curriculum learning — agents level up through increasingly difficult challenges
- **HIVE** (Planned): Swarm intelligence — leaderless emergent convergence
- **FORGE** (Planned): Adversarial refinement — critic-driven iterative improvement
- **HEIST** (Planned): Adaptive workflows — dependency-aware replanning on failure

All built on the shared `dynabots-core` protocols. All independently installable. Mix and match.

---

## SAO: Survival Optimized Arena

**Survival RL + Curriculum Learning**

Agents progress through increasingly difficult challenges. Failure on easy levels blocks advancement.

### Concept

```
Easy Level        Medium Level      Hard Level        Expert Level
[agent test]  --> [agent test]  --> [agent test]  --> [agent test]

Pass? +0.5        Pass? +1.0        Pass? +2.0        Pass? +5.0
Fail? Retry       Fail? Back 1      Fail? Back 2      Fail? Back 3
```

### Use Cases

- **Iterative improvement**: Agents improve by tackling progressively harder tasks
- **Safety testing**: Agents prove competence at lower levels before access to higher
- **Training data generation**: Agents produce labeled training data at each level
- **Skill development**: Agents can specialize in different level ranges

### Example

```python
from dynabots_sao import Arena, CurriculumConfig

config = CurriculumConfig(
    levels=[
        {"difficulty": 0, "timeout_ms": 5000},
        {"difficulty": 1, "timeout_ms": 3000},
        {"difficulty": 2, "timeout_ms": 1000},
        {"difficulty": 3, "timeout_ms": 500},
    ]
)

arena = Arena(
    agents=[agent1, agent2],
    config=config,
)

# Agents compete at each level
result = await arena.progress()
```

---

## HIVE: Swarm Intelligence

**Leaderless Emergent Convergence**

Agents coordinate without central authority. Collective intelligence emerges from local interactions.

### Concept

- No single leader
- Agents communicate via a message bus
- Decisions made by consensus or stigmergy
- Convergence to optimal solutions emerges

### Use Cases

- **Distributed consensus**: Agents vote on decisions
- **Collective problem-solving**: Agents share solutions and refine
- **Adaptive load balancing**: Work redistributes based on capacity
- **Fault tolerance**: System continues if individual agents fail

### Example

```python
from dynabots_hive import Swarm, SwarmConfig

swarm = Swarm(
    agents=[agent1, agent2, agent3, agent4],
    message_bus=memory_bus,  # Shared communication
    config=SwarmConfig(consensus_threshold=0.7)
)

# Agents vote and converge
decision = await swarm.decide("what should we do?")
print(decision)  # Consensus result
```

---

## FORGE: Adversarial Refinement

**Critic-Driven Iterative Improvement**

Agents are refined through adversarial feedback. Critics attack outputs, agents improve.

### Concept

- **Generator**: Creates solutions
- **Critic**: Evaluates and identifies weaknesses
- **Feedback loop**: Generator improves based on criticism
- **Convergence**: Solutions improve with each iteration

### Use Cases

- **Prompt optimization**: Find better prompts through iterative feedback
- **Code improvement**: Critic identifies bugs, agent fixes them
- **Adversarial testing**: Security testing via automated attacks
- **Creative refinement**: Iterate on outputs until acceptable

### Example

```python
from dynabots_forge import Arena, CriticConfig

arena = Arena(
    generator=my_agent,
    critics=[security_critic, quality_critic, efficiency_critic],
    max_iterations=5,
)

# Agent iterates based on criticism
final_solution = await arena.refine("Generate Python code that...")
print(final_solution)
```

---

## HEIST: Adaptive Workflows

**Dependency-Aware Replanning on Failure**

Complex multi-agent workflows that adapt when tasks fail.

### Concept

- **DAG of tasks**: Define task dependencies
- **Smart execution**: Execute tasks respecting dependencies
- **Failure detection**: Detect when tasks fail
- **Replanning**: Automatically adjust plan when failures occur
- **Adaptive strategy**: Choose different agents based on what failed

### Use Cases

- **Enterprise automation**: Multi-step processes with fallbacks
- **Data pipelines**: Handle failures in ETL workflows
- **Complex orchestration**: Agent task dependencies and recovery
- **Cost optimization**: Replan to minimize cost when options available

### Example

```python
from dynabots_heist import Workflow

workflow = Workflow()

# Define tasks with dependencies
workflow.add_task("fetch_data", agent=data_agent)
workflow.add_task("validate", depends_on=["fetch_data"], agent=validator)
workflow.add_task("process", depends_on=["validate"], agent=processor)
workflow.add_task("report", depends_on=["process"], agent=reporter)

# Add fallback strategies
workflow.add_fallback("fetch_data", backup_agent=cached_agent)
workflow.add_fallback("process", backup_agent=fast_processor)

# Execute with automatic replanning
result = await workflow.execute()
```

---

## Timeline (Estimated)

- **Q1 2024**: dynabots-core (in progress)
- **Q2 2024**: dynabots-orc (stable)
- **Q3 2024**: dynabots-sao (alpha)
- **Q4 2024**: dynabots-hive (alpha)
- **Q1 2025**: dynabots-forge (alpha)
- **Q2 2025**: dynabots-heist (alpha)

All packages available on PyPI when ready.

---

## Design Principles

All packages follow these principles:

### Protocol-First

Built on `dynabots-core` protocols. Maximum interoperability.

### Zero Dependencies (Core)

`dynabots-core` has zero external dependencies. Packages may add optional deps.

### Independent Install

Each package is independently installable. Use just what you need.

### Mix and Match

Combine orchestration philosophies. Use ORC for some domains, SAO for others.

### Extensible

Implement protocols to integrate your own orchestration strategies.

---

## Contributing

Interested in contributing? See [CONTRIBUTING.md](https://github.com/Lumi-node/Dynabots/blob/main/CONTRIBUTING.md).

Areas for contribution:

- Protocol implementations
- Additional LLM provider adapters
- New judge strategies
- Storage backends
- Documentation and examples

---

## License

All packages under Apache 2.0.

---

## See Also

- [ORC: Current Package](orc.md)
- [dynabots-core Protocols](../protocols/agent.md)
- [GitHub: Dynabots](https://github.com/Lumi-node/Dynabots)
