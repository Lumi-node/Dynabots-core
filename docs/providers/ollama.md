# Ollama Provider

Local LLMs using Ollama. Best for development and privacy-sensitive workloads.

---

## Installation

```bash
# Install ollama Python package
pip install dynabots-core[ollama]

# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

---

## Setup

### Start Ollama

In a terminal:

```bash
ollama serve
```

Ollama listens on `http://localhost:11434` by default.

### Pull a Model

In another terminal:

```bash
# Recommended: Qwen for best reasoning and tool use
ollama pull qwen2.5:7b

# Or other models
ollama pull llama3.1:70b
ollama pull mixtral:8x22b
```

### List Models

```bash
ollama list
```

---

## Usage

### Basic

```python
from dynabots_core.providers import OllamaProvider
from dynabots_core import LLMMessage

llm = OllamaProvider(model="qwen2.5:7b")

response = await llm.complete([
    LLMMessage(role="system", content="You are helpful."),
    LLMMessage(role="user", content="What is 2+2?"),
])

print(response.content)  # "4"
```

### Custom Server

```python
llm = OllamaProvider(
    model="qwen2.5:72b",
    host="http://gpu-server:11434"  # Custom host
)
```

### With Options

```python
llm = OllamaProvider(
    model="qwen2.5:72b",
    options={
        "num_gpu": 2,      # Use 2 GPUs
        "num_ctx": 8192,   # Context window
        "temperature": 0.7,
    }
)
```

---

## Features

### Temperature

Control randomness:

```python
# Deterministic
response = await llm.complete(messages, temperature=0.0)

# Creative
response = await llm.complete(messages, temperature=0.9)
```

### Max Tokens

Limit response length:

```python
response = await llm.complete(
    messages,
    max_tokens=500
)
```

### JSON Mode

Request JSON output:

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

Enable function calling (model-dependent):

```python
from dynabots_core.protocols.llm import ToolDefinition

tools = [
    ToolDefinition(
        name="search",
        description="Search the knowledge base",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    )
]

response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="Search for Python")
    ],
    tools=tools
)

if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool: {call['function']['name']}")
```

---

## Recommended Models

### For Agents (Best Overall)

- **qwen2.5:72b** - Excellent reasoning, tool use, code
- **qwen2.5:7b** - Smaller, faster (testing)
- **llama3.1:70b** - Strong reasoning, good tool use

### For Code

- **codellama:70b** - Best for code generation
- **qwen2.5:72b** - Also very good for code

### Fast & Cheap

- **mixtral:8x22b** - Fast, good quality
- **neural-chat:7b** - Very fast, decent quality

### Long Context

- **qwen2.5:72b** - Handles 8K+ context
- **llama3.1:70b** - 8K context

---

## Performance Tuning

### GPU Usage

```python
llm = OllamaProvider(
    model="qwen2.5:72b",
    options={
        "num_gpu": -1,  # Use all GPUs
        "num_ctx": 8192,
    }
)
```

### CPU Fallback

If no GPU:

```python
llm = OllamaProvider(
    model="qwen2.5:7b",  # Smaller model
    options={
        "num_threads": 8,  # CPU threads
    }
)
```

### Batch Processing

For multiple requests:

```python
# Ollama keeps model in memory after first use
response1 = await llm.complete(messages1)  # Slow (load model)
response2 = await llm.complete(messages2)  # Fast (model cached)
response3 = await llm.complete(messages3)  # Fast
```

---

## Protocol Definition

::: dynabots_core.providers.ollama.OllamaProvider

---

## Helper Methods

### List Models

```python
models = await llm.list_models()
print(models)  # ["qwen2.5:7b", "llama3.1:70b", ...]
```

### Pull Model

```python
await llm.pull_model("qwen2.5:72b")
```

---

## Common Issues

### Connection Refused

```
Error: Failed to connect to Ollama
```

**Solution**: Start Ollama service:

```bash
ollama serve
```

### Model Not Found

```
Error: model qwen2.5:7b not found
```

**Solution**: Pull the model:

```bash
ollama pull qwen2.5:7b
```

### Out of Memory

```
Error: CUDA out of memory
```

**Solution**: Use a smaller model or increase context timeout:

```python
llm = OllamaProvider(
    model="qwen2.5:7b",  # Smaller
    options={"num_gpu": 1}  # Fewer GPUs
)
```

### Slow Responses

**Cause**: Model running on CPU

**Solution**: Check GPU usage:

```bash
ollama ps  # See running models
```

Install GPU support or use smaller model.

---

## Docker

Run Ollama in Docker:

```bash
docker run -d --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  ollama/ollama
```

Then pull models:

```bash
docker exec <container> ollama pull qwen2.5:7b
```

Use with custom host:

```python
llm = OllamaProvider(
    model="qwen2.5:7b",
    host="http://docker-host:11434"
)
```

---

## See Also

- [Provider Overview](overview.md)
- [LLM Protocol](../protocols/llm.md)
- [Quick Start](../getting-started/quick-start.md)
- [Ollama Website](https://ollama.ai)
