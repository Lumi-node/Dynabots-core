"""
DynaBots Core - LLM Providers Example

Demonstrates using different LLM providers with the unified interface.

Run with:
    python core_providers_example.py
"""

import asyncio
from dynabots_core import LLMMessage


async def demo_ollama():
    """Demonstrate Ollama provider (local LLMs)."""
    print("\n" + "=" * 50)
    print("OLLAMA PROVIDER (Local LLM)")
    print("=" * 50)

    try:
        from dynabots_core.providers import OllamaProvider

        # Initialize with a local model
        llm = OllamaProvider(model="qwen2.5:7b")  # Use smaller model for demo

        # Simple completion
        response = await llm.complete([
            LLMMessage(role="system", content="You are a helpful assistant. Be concise."),
            LLMMessage(role="user", content="What is 2 + 2?"),
        ])

        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")

    except ImportError:
        print("Ollama not installed. Run: pip install ollama")
    except Exception as e:
        print(f"Ollama error: {e}")
        print("Make sure Ollama is running: ollama serve")


async def demo_openai():
    """Demonstrate OpenAI provider."""
    print("\n" + "=" * 50)
    print("OPENAI PROVIDER")
    print("=" * 50)

    try:
        from openai import AsyncOpenAI
        from dynabots_core.providers import OpenAIProvider
        import os

        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY not set. Skipping OpenAI demo.")
            return

        client = AsyncOpenAI()
        llm = OpenAIProvider(client, model="gpt-4o-mini")

        response = await llm.complete([
            LLMMessage(role="system", content="You are a helpful assistant. Be concise."),
            LLMMessage(role="user", content="What is 2 + 2?"),
        ])

        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")

    except ImportError:
        print("OpenAI not installed. Run: pip install openai")
    except Exception as e:
        print(f"OpenAI error: {e}")


async def demo_anthropic():
    """Demonstrate Anthropic provider."""
    print("\n" + "=" * 50)
    print("ANTHROPIC PROVIDER")
    print("=" * 50)

    try:
        from anthropic import AsyncAnthropic
        from dynabots_core.providers import AnthropicProvider
        import os

        # Check for API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ANTHROPIC_API_KEY not set. Skipping Anthropic demo.")
            return

        client = AsyncAnthropic()
        llm = AnthropicProvider(client, model="claude-3-haiku-20240307")

        response = await llm.complete([
            LLMMessage(role="system", content="You are a helpful assistant. Be concise."),
            LLMMessage(role="user", content="What is 2 + 2?"),
        ])

        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")

    except ImportError:
        print("Anthropic not installed. Run: pip install anthropic")
    except Exception as e:
        print(f"Anthropic error: {e}")


async def demo_json_mode():
    """Demonstrate JSON mode for structured output."""
    print("\n" + "=" * 50)
    print("JSON MODE (Structured Output)")
    print("=" * 50)

    try:
        from dynabots_core.providers import OllamaProvider
        import json

        llm = OllamaProvider(model="qwen2.5:7b")

        response = await llm.complete(
            messages=[
                LLMMessage(
                    role="system",
                    content='You extract data. Respond with JSON: {"name": string, "age": number}',
                ),
                LLMMessage(role="user", content="John is 30 years old."),
            ],
            json_mode=True,
        )

        print(f"Raw response: {response.content}")
        try:
            data = json.loads(response.content)
            print(f"Parsed: name={data['name']}, age={data['age']}")
        except json.JSONDecodeError:
            print("Failed to parse JSON")

    except Exception as e:
        print(f"JSON mode error: {e}")


async def main():
    print("DynaBots Core - LLM Providers Demo")
    print("=" * 50)

    await demo_ollama()
    await demo_openai()
    await demo_anthropic()
    await demo_json_mode()

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
