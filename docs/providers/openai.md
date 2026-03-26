# OpenAI Provider

Production-ready access to OpenAI and Azure OpenAI models.

---

## Installation

```bash
pip install dynabots-core[openai]
```

---

## Setup

### OpenAI API Key

```bash
# Get your API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."
```

### Azure OpenAI

```bash
# For Azure OpenAI, also set:
export AZURE_OPENAI_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
```

---

## Usage

### Basic

```python
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider
from dynabots_core import LLMMessage

client = AsyncOpenAI()  # Uses OPENAI_API_KEY env var
llm = OpenAIProvider(client, model="gpt-4o")

response = await llm.complete([
    LLMMessage(role="user", content="What is 2+2?"),
])

print(response.content)  # "4"
```

### Custom API Key

```python
client = AsyncOpenAI(api_key="sk-...")
llm = OpenAIProvider(client, model="gpt-4o")
```

---

## Features

### Temperature

Control randomness:

```python
response = await llm.complete(
    messages,
    temperature=0.1  # Deterministic
)

response = await llm.complete(
    messages,
    temperature=0.9  # Creative
)
```

### Max Tokens

Limit response length:

```python
response = await llm.complete(
    messages,
    max_tokens=100
)
```

### JSON Mode

Structured output:

```python
response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="Extract name and age: ...")
    ],
    json_mode=True
)

import json
data = json.loads(response.content)
```

### Tool Calling

Function calling support:

```python
from dynabots_core.protocols.llm import ToolDefinition

tools = [
    ToolDefinition(
        name="get_weather",
        description="Get current weather",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    )
]

response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="What's the weather in San Francisco?")
    ],
    tools=tools
)

if response.tool_calls:
    for call in response.tool_calls:
        tool_name = call["function"]["name"]
        tool_args = call["function"]["arguments"]
        # Execute tool...
```

---

## Model Selection

### Recommended Models

- **gpt-4o** - Most capable, recommended for production
- **gpt-4o-mini** - Cheaper, still very capable
- **gpt-3.5-turbo** - Older, not recommended for new projects

```python
# Production
llm = OpenAIProvider(client, model="gpt-4o")

# Cost-conscious
llm = OpenAIProvider(client, model="gpt-4o-mini")
```

### Model Comparison

| Model | Cost | Speed | Reasoning | Best For |
|-------|------|-------|-----------|----------|
| gpt-4o | $$$ | Medium | Excellent | Production, complex tasks |
| gpt-4o-mini | $ | Fast | Good | Cost-sensitive, simple tasks |
| gpt-3.5-turbo | $ | Fastest | Basic | Legacy only |

---

## Protocol Definition

::: dynabots_core.providers.openai.OpenAIProvider

---

## Azure OpenAI

Use with Azure-hosted OpenAI:

```python
from openai import AsyncAzureOpenAI
from dynabots_core.providers import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint="https://my-resource.openai.azure.com",
    api_key="your-api-key",
    api_version="2024-02-01",  # Use latest version
)

# Use same provider class
llm = OpenAIProvider(client, model="my-deployment-name")

response = await llm.complete(messages)
```

---

## Cost Optimization

### Model Selection

```python
# Most expensive
llm = OpenAIProvider(client, model="gpt-4o")  # $0.03/$0.06 per 1M tokens

# Cheaper
llm = OpenAIProvider(client, model="gpt-4o-mini")  # $0.15/$0.60 per 1M tokens
```

### Token Limits

```python
# Shorter responses = lower cost
response = await llm.complete(
    messages,
    max_tokens=100  # Limited response
)
```

### Batch Processing

For non-latency-sensitive work, OpenAI offers batch API:

```python
# See OpenAI batch API documentation
# Cheaper rates (~50% discount)
```

---

## Error Handling

```python
try:
    response = await llm.complete(messages)
except Exception as e:
    if "rate_limit" in str(e):
        print("Rate limited, retry later")
    elif "invalid_api_key" in str(e):
        print("Check OPENAI_API_KEY")
    else:
        print(f"Error: {e}")
```

---

## Usage Statistics

OpenAI provides token usage in responses:

```python
response = await llm.complete(messages)

print(response.usage)
# {
#     "prompt_tokens": 50,
#     "completion_tokens": 25,
#     "total_tokens": 75
# }

# Estimate cost
cost = (response.usage["prompt_tokens"] * 0.03 +
        response.usage["completion_tokens"] * 0.06) / 1_000_000
print(f"Cost: ${cost:.6f}")
```

---

## Common Issues

### Invalid API Key

```
Error: Invalid API key provided
```

**Solution**: Check your API key:

```bash
echo $OPENAI_API_KEY
```

Get a new key from [OpenAI dashboard](https://platform.openai.com/api-keys).

### Rate Limiting

```
Error: 429 Rate limit exceeded
```

**Solution**: Implement exponential backoff:

```python
import asyncio

async def call_with_backoff(llm, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await llm.complete(messages)
        except Exception as e:
            if "rate_limit" not in str(e):
                raise
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            await asyncio.sleep(wait)
```

### Quota Exceeded

```
Error: You exceeded your current quota
```

**Solution**: Check your billing and usage at [OpenAI dashboard](https://platform.openai.com/account/billing/overview).

---

## See Also

- [Provider Overview](overview.md)
- [LLM Protocol](../protocols/llm.md)
- [OpenAI Docs](https://platform.openai.com/docs)
