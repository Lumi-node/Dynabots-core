# LLM Provider Protocol

The unified interface for any language model service.

---

## Protocol Definition

::: dynabots_core.protocols.llm.LLMProvider

::: dynabots_core.protocols.llm.LLMMessage

::: dynabots_core.protocols.llm.LLMResponse

::: dynabots_core.protocols.llm.ToolDefinition

---

## Custom Implementation

Create your own provider for any LLM service:

```python
from typing import Any, Dict, List, Optional
from dynabots_core.protocols.llm import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ToolDefinition,
)

class MyCustomProvider:
    """Custom LLM provider for your own service."""

    def __init__(self, api_key: str, model: str = "my-model"):
        self.api_key = api_key
        self.model = model
        self.client = MyLLMClient(api_key)

    async def complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
        tools: Optional[List[ToolDefinition]] = None,
    ) -> LLMResponse:
        """Call your LLM service."""
        # Convert messages to your API format
        api_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        # Build request
        request = {
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            request["response_format"] = "json"

        if tools:
            request["tools"] = [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                }
                for t in tools
            ]

        # Call your LLM service
        response = await self.client.generate(**request)

        # Parse response
        return LLMResponse(
            content=response.text,
            model=self.model,
            usage={
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
            },
        )
```

---

## Message Format

### LLMMessage

Represents a single message in a conversation:

```python
from dynabots_core import LLMMessage

messages = [
    LLMMessage(
        role="system",
        content="You are a helpful assistant."
    ),
    LLMMessage(
        role="user",
        content="What is 2+2?"
    ),
    LLMMessage(
        role="assistant",
        content="2+2 equals 4."
    ),
    LLMMessage(
        role="user",
        content="And 3+3?"
    ),
]
```

Roles:
- `"system"`: System prompt (LLM behavior)
- `"user"`: User input
- `"assistant"`: LLM response
- `"tool"`: Tool output (for tool calling)

### LLMResponse

The response from a provider:

```python
response = await provider.complete(messages)

print(response.content)           # The LLM's response text
print(response.model)              # Model identifier
print(response.usage)              # {"prompt_tokens": N, "completion_tokens": N, "total_tokens": N}
print(response.finish_reason)      # "stop", "length", "tool_calls"
print(response.tool_calls)         # Tool calls if any
```

---

## Features

### Temperature

Control randomness:

```python
# Deterministic (for analysis, code generation)
response = await llm.complete(messages, temperature=0.0)

# Balanced (default)
response = await llm.complete(messages, temperature=0.1)

# Creative (for brainstorming)
response = await llm.complete(messages, temperature=0.9)
```

### JSON Mode

Request structured JSON output:

```python
response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="Extract: name, age, role from the text...")
    ],
    json_mode=True,  # Request JSON output
)

import json
data = json.loads(response.content)
print(data)  # {"name": "Alice", "age": 30, "role": "Engineer"}
```

Not all providers support JSON mode. Check provider documentation.

### Max Tokens

Limit response length:

```python
# Short responses
response = await llm.complete(messages, max_tokens=100)

# Long responses
response = await llm.complete(messages, max_tokens=4000)
```

### Tool Calling

Enable function calling:

```python
from dynabots_core.protocols.llm import ToolDefinition

tools = [
    ToolDefinition(
        name="search",
        description="Search the knowledge base",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    ),
    ToolDefinition(
        name="calculate",
        description="Perform calculations",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"}
            },
            "required": ["expression"]
        }
    ),
]

response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="What is 2+2 and search for Python?")
    ],
    tools=tools,
)

if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool: {call['function']['name']}")
        print(f"Args: {call['function']['arguments']}")
```

---

## Built-in Providers

DynaBots provides three implementations.

### Ollama (Local)

```python
from dynabots_core.providers import OllamaProvider

llm = OllamaProvider(model="qwen2.5:72b")
response = await llm.complete(messages)
```

Best for:
- Local development
- Privacy-sensitive workloads
- Self-hosted deployments

Requires: Ollama running locally

### OpenAI (Cloud)

```python
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider

client = AsyncOpenAI(api_key="sk-...")
llm = OpenAIProvider(client, model="gpt-4o")
response = await llm.complete(messages)
```

Best for:
- Production workloads
- Advanced capabilities
- High-quality outputs

Also supports Azure OpenAI endpoint.

### Anthropic (Cloud)

```python
from anthropic import AsyncAnthropic
from dynabots_core.providers import AnthropicProvider

client = AsyncAnthropic(api_key="sk-ant-...")
llm = AnthropicProvider(client, model="claude-3-5-sonnet-20241022")
response = await llm.complete(messages)
```

Best for:
- Constitutional AI
- Extended thinking (with claude models)
- Multimodal understanding

---

## Comparison

| Provider | Cost | Speed | Customization | Latency |
|----------|------|-------|---------------|---------|
| Ollama | Free | Medium | Full | Low (local) |
| OpenAI | $$ | Fast | Limited | Medium |
| Anthropic | $$ | Fast | Limited | Medium |

---

## Swapping Providers

The power of protocols: change LLM without changing agent code.

```python
# Start with Ollama (free, local)
llm = OllamaProvider(model="qwen2.5:7b")

# Agent code
async def my_agent_method(self, task):
    response = await self.llm.complete(messages)
    return response.content

# Later, switch to OpenAI
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider

llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

# Same agent code works!
self.llm = llm  # Just swap the provider
```

No agent code changes needed.

---

## Error Handling

Providers raise exceptions on failure:

```python
try:
    response = await llm.complete(messages)
except ConnectionError:
    print("LLM service unreachable")
except ValueError:
    print("Invalid parameters")
except Exception as e:
    print(f"LLM error: {e}")
```

---

## Best Practices

1. **Async/await**: Always use async. Providers are async.
2. **Temperature tuning**: Lower (0.1) for deterministic tasks, higher for creative.
3. **Token limits**: Set reasonable max_tokens to control costs.
4. **Error handling**: Wrap provider calls in try/except.
5. **Fallbacks**: Have a fallback provider if a service is down.

---

## See Also

- [Core Concepts: LLMProvider](../getting-started/concepts.md#llmprovider)
- [Provider Overview](../providers/overview.md)
- [Built-in Providers](../providers/ollama.md)
- [Agent Protocol](agent.md)
