# Anthropic Provider

Claude models from Anthropic. Great for long context and constitutional AI.

---

## Installation

```bash
pip install dynabots-core[anthropic]
```

---

## Setup

### API Key

```bash
# Get your API key from https://console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Usage

### Basic

```python
from anthropic import AsyncAnthropic
from dynabots_core.providers import AnthropicProvider
from dynabots_core import LLMMessage

client = AsyncAnthropic()  # Uses ANTHROPIC_API_KEY env var
llm = AnthropicProvider(client, model="claude-3-5-sonnet-20241022")

response = await llm.complete([
    LLMMessage(role="user", content="What is 2+2?"),
])

print(response.content)  # "4"
```

### Custom API Key

```python
client = AsyncAnthropic(api_key="sk-ant-...")
llm = AnthropicProvider(client, model="claude-3-5-sonnet-20241022")
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
    max_tokens=1000
)
```

### System Prompt

Include system instructions:

```python
response = await llm.complete([
    LLMMessage(role="system", content="You are an expert analyst."),
    LLMMessage(role="user", content="Analyze this data..."),
])
```

### Tool Calling

Function calling support:

```python
from dynabots_core.protocols.llm import ToolDefinition

tools = [
    ToolDefinition(
        name="calculate",
        description="Perform mathematical calculations",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]
        }
    )
]

response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="What is 123 + 456?")
    ],
    tools=tools
)

if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool: {call['function']['name']}")
        print(f"Args: {call['function']['arguments']}")
```

---

## Model Selection

### Recommended Models

- **claude-3-5-sonnet-20241022** - Best overall, recommended
- **claude-3-haiku-20240307** - Cheaper, lighter
- **claude-3-opus-20240229** - Most powerful, expensive

```python
# Recommended
llm = AnthropicProvider(
    client,
    model="claude-3-5-sonnet-20241022"
)

# Budget
llm = AnthropicProvider(
    client,
    model="claude-3-haiku-20240307"
)

# Maximum power
llm = AnthropicProvider(
    client,
    model="claude-3-opus-20240229"
)
```

### Model Comparison

| Model | Cost | Speed | Context | Best For |
|-------|------|-------|---------|----------|
| claude-3-5-sonnet | $$ | Medium | 200K | Production, balanced |
| claude-3-haiku | $ | Fast | 200K | Cost-sensitive |
| claude-3-opus | $$$ | Slow | 200K | Complex reasoning |

---

## Long Context

Claude models support 200K token context window:

```python
# You can fit a lot of context
very_long_text = """
[200,000 tokens of text, documents, conversations, etc.]
"""

response = await llm.complete([
    LLMMessage(
        role="user",
        content=f"Analyze this: {very_long_text}"
    )
])
```

Great for:
- Analyzing large documents
- Full conversation history
- Knowledge base retrieval augmentation

---

## Protocol Definition

::: dynabots_core.providers.anthropic.AnthropicProvider

---

## Constitutional AI

Claude is trained with constitutional AI—it follows principles of helpfulness, harmlessness, and honesty:

```python
response = await llm.complete([
    LLMMessage(role="user", content="How do I make an illegal substance?"),
])

# Claude will decline and offer helpful alternatives
```

This is built-in, no configuration needed.

---

## Cost Optimization

### Model Selection

```python
# Most expensive
llm = AnthropicProvider(client, model="claude-3-opus-20240229")
# $0.015 per 1M input tokens, $0.075 per 1M output

# Recommended (best value)
llm = AnthropicProvider(client, model="claude-3-5-sonnet-20241022")
# $0.003 per 1M input tokens, $0.015 per 1M output

# Cheapest
llm = AnthropicProvider(client, model="claude-3-haiku-20240307")
# $0.00080 per 1M input tokens, $0.0024 per 1M output
```

### Token Limits

```python
# Keep responses short to save money
response = await llm.complete(
    messages,
    max_tokens=500  # Limited response
)
```

---

## Error Handling

```python
try:
    response = await llm.complete(messages)
except Exception as e:
    if "invalid_request_error" in str(type(e)):
        print("Check message format")
    elif "authentication_error" in str(type(e)):
        print("Check API key")
    else:
        print(f"Error: {e}")
```

---

## Usage Statistics

Anthropic provides token usage:

```python
response = await llm.complete(messages)

print(response.usage)
# {
#     "prompt_tokens": 100,
#     "completion_tokens": 50,
#     "total_tokens": 150
# }

# Estimate cost (Claude 3.5 Sonnet)
cost = (response.usage["prompt_tokens"] * 0.003 +
        response.usage["completion_tokens"] * 0.015) / 1_000_000
print(f"Cost: ${cost:.6f}")
```

---

## Common Issues

### Invalid API Key

```
Error: Invalid API key
```

**Solution**: Check your API key:

```bash
echo $ANTHROPIC_API_KEY
```

Get a new key from [Anthropic console](https://console.anthropic.com).

### Quota Exceeded

```
Error: You exceeded your quota
```

**Solution**: Check usage at [Anthropic console](https://console.anthropic.com/account/billing/overview).

### Message Too Long

```
Error: Message is too long
```

**Solution**: Claude has a max input/output tokens. Reduce context or response limit:

```python
response = await llm.complete(
    messages,
    max_tokens=1000  # Be explicit
)
```

---

## Tips

1. **System prompts**: Use them to set behavior and context.
2. **Long context**: Leverage the 200K context for rich documents.
3. **JSON mode**: No native JSON mode, use structured prompts.
4. **Tool calling**: Works well with Claude—models are good at planning.

---

## See Also

- [Provider Overview](overview.md)
- [LLM Protocol](../protocols/llm.md)
- [Anthropic Docs](https://docs.anthropic.com)
