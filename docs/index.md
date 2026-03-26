---
hide:
  - navigation
  - toc
---

<style>
  .md-typeset h1 { display: none; }
</style>

<div class="hero" markdown>

# **DynaBots**

### Multi-agent orchestration for Python.

A protocol-first foundation for building, evaluating, and deploying AI agent systems.
Zero dependencies. Any LLM. Multiple orchestration philosophies.

[Get Started](getting-started/installation.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/Lumi-node/Dynabots-core){ .md-button }

</div>

---

<div class="grid cards" markdown>

-   :material-protocol:{ .lg .middle } **Protocol-First**

    ---

    No base classes. No framework lock-in. Just implement the right methods
    using Python's structural subtyping and your class works everywhere.

    [:octicons-arrow-right-24: Learn the protocols](getting-started/concepts.md)

-   :material-swap-horizontal:{ .lg .middle } **Any LLM**

    ---

    Unified interface for Ollama (local, free), OpenAI, and Anthropic.
    Swap providers without changing your agent code.

    [:octicons-arrow-right-24: Provider guide](providers/overview.md)

-   :material-sword-cross:{ .lg .middle } **ORC — Competitive Orchestration**

    ---

    Agents compete for domain leadership in the Arena.
    The best performer earns the crown — until challenged.

    [:octicons-arrow-right-24: Explore ORC](ecosystem/orc.md)

-   :material-puzzle:{ .lg .middle } **Composable Ecosystem**

    ---

    `dynabots-core` provides the foundation. Orchestration packages layer on top.
    Each independently installable. All share the same protocols.

    [:octicons-arrow-right-24: See the roadmap](ecosystem/roadmap.md)

</div>

---

## Quick Example

=== "Define an Agent"

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

=== "Use Any LLM"

    ```python
    from dynabots_core.providers import OllamaProvider, OpenAIProvider, AnthropicProvider

    # Local (free)
    llm = OllamaProvider(model="qwen2.5:7b")

    # OpenAI
    from openai import AsyncOpenAI
    llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

    # Anthropic
    from anthropic import AsyncAnthropic
    llm = AnthropicProvider(AsyncAnthropic(), model="claude-sonnet-4-20250514")
    ```

=== "Run an Arena (ORC)"

    ```python
    from dynabots_orc import Arena, MetricsJudge

    arena = Arena(
        agents=[DataAgent(), AnalyticsAgent()],
        judge=MetricsJudge(),
        on_succession=lambda old, new, d: print(f"{new} defeats {old}!"),
    )

    result = await arena.process("Analyze Q4 sales data")
    print(f"Winner: {result.winner}")
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
   │   ORC    │ │  [SAO]   │ │ [FORGE]  │
   │  Arena   │ │  Tower   │ │  Anvil   │
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

---

## Packages

| Package | Install | Description |
|---------|---------|-------------|
| **dynabots-core** | `pip install dynabots-core` | Protocols, LLM providers, TaskResult |
| **orc-arena** | `pip install orc-arena` | Competitive orchestration — agents fight for leadership |
| *SAO* | *coming soon* | Survival RL — agents level up through challenge floors |
| *FORGE* | *coming soon* | Adversarial refinement — critic-driven improvement |
| *HIVE* | *coming soon* | Swarm intelligence — leaderless emergent convergence |

---

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Documentation**

    ---

    [:octicons-arrow-right-24: Getting Started](getting-started/installation.md)
    [:octicons-arrow-right-24: Protocol Reference](protocols/agent.md)
    [:octicons-arrow-right-24: Provider Guide](providers/overview.md)
    [:octicons-arrow-right-24: TaskResult Semantics](value-objects/task-result.md)

-   :material-github:{ .lg .middle } **Community**

    ---

    [:octicons-arrow-right-24: GitHub](https://github.com/Lumi-node/Dynabots-core)
    [:octicons-arrow-right-24: PyPI — dynabots-core](https://pypi.org/project/dynabots-core/)
    [:octicons-arrow-right-24: PyPI — orc-arena](https://pypi.org/project/orc-arena/)
    [:octicons-arrow-right-24: ORC Docs](https://lumi-node.github.io/ORC/)

</div>
