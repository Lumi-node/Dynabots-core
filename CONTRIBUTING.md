# Contributing to DynaBots

Thank you for your interest in contributing to DynaBots!

## Getting Started

1. **Fork the repository** and clone your fork
2. **Install dependencies**:
   ```bash
   cd dynabots
   pip install -r requirements.txt
   ```
3. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

## Development Workflow

### Code Style

- We use **Ruff** for linting and formatting
- Run `ruff check .` before committing
- Run `ruff format .` to auto-format code

### Type Hints

- Use type hints for all function signatures
- Use `mypy` for static type checking

### Commit Messages

- Use clear, descriptive commit messages
- Format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Example:
```
feat: add parallel execution support to orchestrator
fix: resolve race condition in DAG builder
docs: update README with benchmark results
```

## Adding New Agents

1. Create a new adapter in `adapters/`
2. Define tools in `tools/`
3. Add tests in `tests/`
4. Update documentation

Example agent structure:
```python
from adapters.zeroclaw_adapter import MockZeroClawAdapter

agents["NewAgent"] = MockZeroClawAdapter(
    name="NewAgent",
    description="What this agent does",
    capabilities=["capability1", "capability2"],
    tools=[...],
)
```

## Adding New Tools

Tools follow a simple schema:
```python
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict = None
```

## Running Benchmarks

```bash
# Heuristic mode (no API keys)
python run_benchmark.py

# LLM mode (requires ANTHROPIC_API_KEY)
python run_benchmark.py --llm

# Specific complexity
python run_benchmark.py --complexity complex --llm -v
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `ruff check .`
5. Push and create a PR

## Questions?

Open an issue or start a discussion on GitHub.
