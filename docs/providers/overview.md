# LLM Providers Overview

DynaBots provides unified access to multiple LLM services through the `LLMProvider` protocol.

---

## Comparison

| Provider | Cost | Setup | Latency | Customization | Best For |
|----------|------|-------|---------|---------------|----------|
| **Ollama** | Free | Self-hosted | Low (local) | Full control | Development, local testing, privacy |
| **OpenAI** | $$$ | Cloud API | ~1s | Limited | Production, advanced models |
| **Anthropic** | $$$ | Cloud API | ~1-2s | Limited | Constitutional AI, long context |

---

## Quick Start

### Ollama (Local)

Best for development and testing.

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# In another terminal, pull a model
ollama pull qwen2.5:7b
```

Then in Python:

```python
from dynabots_core.providers import OllamaProvider

llm = OllamaProvider(model="qwen2.5:7b")
response = await llm.complete([...])
```

### OpenAI (Cloud)

Production-ready, highest capabilities.

```bash
pip install dynabots-core[openai]
export OPENAI_API_KEY="sk-..."
```

```python
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider

client = AsyncOpenAI()
llm = OpenAIProvider(client, model="gpt-4o")
response = await llm.complete([...])
```

### Anthropic (Cloud)

Good for long-context and constitutional AI.

```bash
pip install dynabots-core[anthropic]
export ANTHROPIC_API_KEY="sk-ant-..."
```

```python
from anthropic import AsyncAnthropic
from dynabots_core.providers import AnthropicProvider

client = AsyncAnthropic()
llm = AnthropicProvider(client, model="claude-3-5-sonnet-20241022")
response = await llm.complete([...])
```

---

## Feature Matrix

| Feature | Ollama | OpenAI | Anthropic |
|---------|--------|--------|-----------|
| **Temperature** | Yes | Yes | Yes |
| **JSON Mode** | Yes | Yes | No* |
| **Tool Calling** | Yes* | Yes | Yes |
| **Token Counting** | No | No | Yes |
| **Vision** | Some models | Yes | Yes |
| **Streaming** | Yes | Yes | Yes |
| **Local** | Yes | No | No |
| **Free** | Yes | No | No |

\* Partial support, model-dependent

---

## Model Recommendations

### Ollama Models (Local)

- **qwen2.5:72b** - Best overall for agent reasoning and tool use
- **llama3.1:70b** - Strong reasoning, good tool use
- **mixtral:8x22b** - Fast, good balance
- **codellama:70b** - Code generation

Start with **qwen2.5:7b** for testing (small, fast).

### OpenAI Models (Cloud)

- **gpt-4o** - Most capable, recommended
- **gpt-4o-mini** - Cheaper, still strong
- **gpt-3.5-turbo** - Legacy, not recommended

### Anthropic Models (Cloud)

- **claude-3-5-sonnet-20241022** - Best overall
- **claude-3-haiku-20240307** - Cheaper, lighter
- **claude-3-opus-20240229** - Most powerful, expensive

---

## Switching Providers

One of the key benefits of protocols: swap providers without changing agent code.

```python
# Start with Ollama
llm = OllamaProvider(model="qwen2.5:7b")

# Agent code
async def my_agent_method(self):
    response = await self.llm.complete(messages)
    return response.content

# Later, scale to production
from openai import AsyncOpenAI
from dynabots_core.providers import OpenAIProvider

llm = OpenAIProvider(AsyncOpenAI(), model="gpt-4o")

# Same agent code! Just swap the provider
self.llm = llm
```

---

## Cost Considerations

### Ollama

- **Cost**: Free (hardware only)
- **Best for**: Development, prototyping, local use cases
- **Trade-off**: Lower model quality, requires GPU/CPU

### OpenAI

- **Input cost**: $0.03 per 1M tokens (GPT-4o)
- **Output cost**: $0.06 per 1M tokens (GPT-4o)
- **Best for**: Production, where quality matters
- **Trade-off**: API costs scale with usage

### Anthropic

- **Input cost**: $0.003 per 1M tokens (Claude 3.5 Sonnet)
- **Output cost**: $0.015 per 1M tokens
- **Best for**: Long-context applications
- **Trade-off**: Slightly different API patterns

---

## Environment Setup

### Ollama

```bash
# Download from https://ollama.ai
# Extract and run:
ollama serve

# Test
curl http://localhost:11434
```

### OpenAI

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Test
python -c "from openai import AsyncOpenAI; print('OK')"
```

### Anthropic

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Test
python -c "from anthropic import AsyncAnthropic; print('OK')"
```

---

## Error Handling

```python
from dynabots_core.providers import OllamaProvider

try:
    llm = OllamaProvider(model="qwen2.5:7b")
    response = await llm.complete(messages)
except ConnectionError:
    print("Ollama service not running")
except Exception as e:
    print(f"LLM error: {e}")
```

---

## Azure OpenAI

Also supported with OpenAI provider:

```python
from openai import AsyncAzureOpenAI
from dynabots_core.providers import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint="https://my-resource.openai.azure.com",
    api_key="...",
    api_version="2024-02-01",
)

llm = OpenAIProvider(client, model="my-deployment-name")
```

---

## Custom Provider

Implement the `LLMProvider` protocol for your service:

```python
from dynabots_core.protocols.llm import LLMProvider, LLMMessage, LLMResponse

class MyLLMProvider:
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
        tools = None,
    ) -> LLMResponse:
        # Call your LLM service
        # Return LLMResponse
        ...
```

See [LLM Provider Protocol](../protocols/llm.md) for details.

---

## See Also

- [Ollama Provider](ollama.md)
- [OpenAI Provider](openai.md)
- [Anthropic Provider](anthropic.md)
- [LLM Protocol](../protocols/llm.md)
