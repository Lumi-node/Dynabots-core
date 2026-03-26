# Installation

## Basic Install

Install the core package:

```bash
pip install dynabots-core
```

Verify installation:

```bash
python -c "from dynabots_core import Agent, TaskResult; print('Ready')"
```

---

## Provider Extras

DynaBots uses optional dependencies. Install only the providers you need.

### Ollama (Local Models)

```bash
pip install dynabots-core[ollama]
```

Requires: [Ollama](https://ollama.ai) installed and running locally.

### OpenAI

```bash
pip install dynabots-core[openai]
```

### Anthropic

```bash
pip install dynabots-core[anthropic]
```

### All Providers

```bash
pip install dynabots-core[all]
```

---

## Development Install

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Lumi-node/Dynabots.git
cd Dynabots

# Install core in development mode
pip install -e "packages/core[dev]"

# Run tests
pytest packages/core/tests/ -v
```

---

## Orchestration Packages

### ORC Arena

For competitive agent orchestration:

```bash
pip install dynabots-orc
```

### Future Packages

More orchestration philosophies coming soon:

- **SAO**: Survival RL / Curriculum Learning
- **HIVE**: Swarm Intelligence
- **FORGE**: Adversarial Refinement
- **HEIST**: Adaptive Workflows

All built on the `dynabots-core` foundation.

---

## Environment Setup

### Ollama

1. [Install Ollama](https://ollama.ai)
2. Start the service:
   ```bash
   ollama serve
   ```
3. Pull a model:
   ```bash
   ollama pull qwen2.5:7b
   ```

### OpenAI

Set your API key:

```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic

Set your API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## System Requirements

- Python 3.10+
- No external system dependencies for core package
- Optional: Docker/GPU for Ollama with GPU acceleration

---

## Troubleshooting

### "Module not found" for providers

Install the provider you're using:

```bash
# For Ollama
pip install ollama

# For OpenAI
pip install openai

# For Anthropic
pip install anthropic
```

### Ollama connection failed

Make sure Ollama is running:

```bash
# Start Ollama service
ollama serve

# In another terminal, test connectivity
curl http://localhost:11434
```

### API authentication errors

Verify your API keys are set in environment variables:

```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```
