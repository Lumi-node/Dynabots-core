# Quick Start

Get your first agent running in 5 minutes.

---

## Step 1: Install

```bash
pip install dynabots-core[ollama]
```

---

## Step 2: Start Ollama

In a terminal, start the Ollama service:

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull qwen2.5:7b
```

---

## Step 3: Create Your Agent

Create a file named `my_agent.py`:

```python
import asyncio
from typing import Any, Dict, List

from dynabots_core import Agent, TaskResult, LLMMessage
from dynabots_core.providers import OllamaProvider


class SearchAgent:
    """Simple agent that searches a local knowledge base."""

    def __init__(self):
        self.knowledge_base = {
            "Python": "A high-level programming language",
            "Rust": "A systems programming language with memory safety",
            "Go": "A concurrent programming language by Google",
        }
        self.llm = OllamaProvider(model="qwen2.5:7b")

    @property
    def name(self) -> str:
        return "SearchAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["search", "explain"]

    @property
    def domains(self) -> List[str]:
        return ["programming", "languages"]

    async def process_task(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> TaskResult:
        """Process a task using the LLM."""
        task_id = context.get("task_id", "unknown")

        # Prepare knowledge base for LLM
        knowledge_str = "\n".join(
            [f"- {k}: {v}" for k, v in self.knowledge_base.items()]
        )

        prompt = f"""You are a helpful assistant with knowledge of programming languages.

Available information:
{knowledge_str}

User request: {task_description}

Provide a helpful response based on the knowledge base."""

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
        return True


async def main():
    # Create agent
    agent = SearchAgent()

    # Test the agent
    tasks = [
        "What is Python?",
        "Compare Rust and Go",
        "Explain memory safety",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task}")
        result = await agent.process_task(task, {"task_id": f"task_{i}"})

        if result.is_success:
            print(f"Response: {result.data['response']}")
        else:
            print(f"Error: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 4: Run Your Agent

```bash
python my_agent.py
```

You should see output like:

```
Task 1: What is Python?
Response: Python is a high-level, interpreted programming language known for its simplicity and readability...

Task 2: Compare Rust and Go
Response: Rust is a systems language with strong memory safety guarantees, while Go is focused on concurrency...

Task 3: Explain memory safety
Response: Memory safety refers to the prevention of memory-related errors...
```

---

## Step 5: Swap Providers (Optional)

Try a different LLM provider without changing your agent code.

### Use OpenAI

```bash
pip install dynabots-core[openai]
export OPENAI_API_KEY="sk-..."
```

Update `my_agent.py`:

```python
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider

# Change initialization
self.llm = OpenAIProvider(
    AsyncOpenAI(),
    model="gpt-4o-mini"
)
```

Run the same code. Your agent works without changes.

### Use Anthropic

```bash
pip install dynabots-core[anthropic]
export ANTHROPIC_API_KEY="sk-ant-..."
```

Update `my_agent.py`:

```python
from anthropic import AsyncAnthropic
from dynabots_core.providers import AnthropicProvider

# Change initialization
self.llm = AnthropicProvider(
    AsyncAnthropic(),
    model="claude-3-5-sonnet-20241022"
)
```

Same agent, different LLM. That's the power of protocols.

---

## What's Next?

- Learn about [Core Concepts](concepts.md)
- Read the [Agent Protocol](../protocols/agent.md) documentation
- Explore [LLM Providers](../providers/overview.md)
- Try [ORC competitive orchestration](../ecosystem/orc.md)

---

## Troubleshooting

### ImportError: ollama not found

Install Ollama provider:

```bash
pip install ollama
```

### Connection refused (Ollama)

Make sure Ollama is running:

```bash
ollama serve
```

### Model not found

Pull the model:

```bash
ollama pull qwen2.5:7b
```

### API key errors

Check environment variables:

```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```
