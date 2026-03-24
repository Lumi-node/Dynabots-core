"""Tests for LLM providers (mocked, no network calls)."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dynabots_core.protocols.llm import LLMMessage, LLMResponse, ToolDefinition
from dynabots_core.providers.openai import OpenAIProvider
from dynabots_core.providers.anthropic import AnthropicProvider
from dynabots_core.providers.ollama import OllamaProvider


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_openai_provider_instantiation(self, mock_openai_client):
        """Test creating an OpenAI provider."""
        provider = OpenAIProvider(mock_openai_client, model="gpt-4o")

        assert provider.model == "gpt-4o"

    @pytest.mark.asyncio
    async def test_openai_complete_basic(self, mock_openai_client):
        """Test basic completion call."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(mock_openai_client, model="gpt-4o")

        response = await provider.complete(
            [LLMMessage(role="user", content="Hello")]
        )

        assert response.content == "Test response"
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 30
        assert response.finish_reason == "stop"
        assert response.tool_calls is None

    @pytest.mark.asyncio
    async def test_openai_complete_with_json_mode(self, mock_openai_client):
        """Test completion with JSON mode."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=5,
            completion_tokens=10,
            total_tokens=15,
        )

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(mock_openai_client)

        response = await provider.complete(
            [LLMMessage(role="user", content="Return JSON")],
            json_mode=True,
        )

        assert response.content == '{"key": "value"}'

        # Verify that json_mode was passed
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert "response_format" in call_kwargs
        assert call_kwargs["response_format"]["type"] == "json_object"

    @pytest.mark.asyncio
    async def test_openai_complete_with_tools(self, mock_openai_client):
        """Test completion with tool definitions."""
        # Mock response with tool calls
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "search"
        mock_tool_call.function.arguments = '{"query": "test"}'

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.usage = MagicMock(
            prompt_tokens=20,
            completion_tokens=15,
            total_tokens=35,
        )

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(mock_openai_client)

        tool_def = ToolDefinition(
            name="search",
            description="Search function",
            parameters={"type": "object"},
        )

        response = await provider.complete(
            [LLMMessage(role="user", content="Search for something")],
            tools=[tool_def],
        )

        assert response.finish_reason == "tool_calls"
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["function"]["name"] == "search"

        # Verify tools were passed
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert "tools" in call_kwargs

    @pytest.mark.asyncio
    async def test_openai_temperature_and_max_tokens(self, mock_openai_client):
        """Test that temperature and max_tokens are passed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = None

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(mock_openai_client)

        await provider.complete(
            [LLMMessage(role="user", content="Test")],
            temperature=0.7,
            max_tokens=500,
        )

        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 500


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_anthropic_provider_instantiation(self, mock_anthropic_client):
        """Test creating an Anthropic provider."""
        provider = AnthropicProvider(mock_anthropic_client, model="claude-3-5-sonnet-20241022")

        assert provider.model == "claude-3-5-sonnet-20241022"

    @pytest.mark.asyncio
    async def test_anthropic_complete_basic(self, mock_anthropic_client):
        """Test basic Anthropic completion."""
        # Mock response
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Claude response"

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_response.usage = MagicMock(
            input_tokens=10,
            output_tokens=15,
        )
        mock_response.stop_reason = "end_turn"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        response = await provider.complete(
            [LLMMessage(role="user", content="Hello")]
        )

        assert response.content == "Claude response"
        assert response.usage["total_tokens"] == 25
        assert response.finish_reason == "end_turn"

    @pytest.mark.asyncio
    async def test_anthropic_system_message_extraction(self, mock_anthropic_client):
        """Test that system messages are extracted and passed separately."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Response"

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=10)
        mock_response.stop_reason = "end_turn"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="Hello"),
        ]

        await provider.complete(messages)

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        # System message should be extracted into "system" kwarg
        assert "system" in call_kwargs
        assert "You are a helpful assistant." in call_kwargs["system"]
        # User message should be in messages
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_anthropic_multiple_system_messages(self, mock_anthropic_client):
        """Test handling multiple system messages."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Response"

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=10)
        mock_response.stop_reason = "end_turn"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        messages = [
            LLMMessage(role="system", content="System part 1"),
            LLMMessage(role="system", content="System part 2"),
            LLMMessage(role="user", content="User message"),
        ]

        await provider.complete(messages)

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        # Both system parts should be concatenated
        assert "System part 1" in call_kwargs["system"]
        assert "System part 2" in call_kwargs["system"]

    @pytest.mark.asyncio
    async def test_anthropic_json_mode(self, mock_anthropic_client):
        """Test JSON mode appends instruction to system prompt."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = '{"result": true}'

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=15)
        mock_response.stop_reason = "end_turn"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        messages = [
            LLMMessage(role="system", content="You are helpful."),
            LLMMessage(role="user", content="Output JSON"),
        ]

        await provider.complete(messages, json_mode=True)

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert "Respond with valid JSON only" in call_kwargs["system"]

    @pytest.mark.asyncio
    async def test_anthropic_tool_calls(self, mock_anthropic_client):
        """Test handling Anthropic tool use blocks."""
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.id = "tool_call_123"
        tool_use_block.name = "search_database"
        tool_use_block.input = {"query": "test query"}

        mock_response = MagicMock()
        mock_response.content = [tool_use_block]
        mock_response.usage = MagicMock(input_tokens=20, output_tokens=10)
        mock_response.stop_reason = "tool_use"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        response = await provider.complete(
            [LLMMessage(role="user", content="Search something")]
        )

        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["function"]["name"] == "search_database"
        assert response.tool_calls[0]["function"]["arguments"] == {"query": "test query"}

    @pytest.mark.asyncio
    async def test_anthropic_mixed_content(self, mock_anthropic_client):
        """Test response with mixed text and tool use."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "I'll search for that."

        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.id = "call_1"
        tool_use_block.name = "search"
        tool_use_block.input = {"q": "something"}

        mock_response = MagicMock()
        mock_response.content = [text_block, tool_use_block]
        mock_response.usage = MagicMock(input_tokens=15, output_tokens=20)
        mock_response.stop_reason = "tool_use"

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(mock_anthropic_client)

        response = await provider.complete(
            [LLMMessage(role="user", content="Search")]
        )

        assert "I'll search for that." in response.content
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1


class TestOllamaProvider:
    """Tests for Ollama provider."""

    @pytest.fixture
    def mock_ollama_client(self):
        """Create a mock Ollama client."""
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_ollama_provider_instantiation(self):
        """Test creating an Ollama provider."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            provider = OllamaProvider(model="llama3.1:70b")

            assert provider.model == "llama3.1:70b"

    @pytest.mark.asyncio
    async def test_ollama_complete_basic(self):
        """Test basic Ollama completion."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = {
                "message": {"content": "Ollama response"},
                "prompt_eval_count": 10,
                "eval_count": 15,
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            provider = OllamaProvider(model="qwen2.5:72b")

            response = await provider.complete(
                [LLMMessage(role="user", content="Hello")]
            )

            assert response.content == "Ollama response"
            assert response.usage["prompt_tokens"] == 10
            assert response.usage["completion_tokens"] == 15
            assert response.usage["total_tokens"] == 25

    @pytest.mark.asyncio
    async def test_ollama_json_mode(self):
        """Test Ollama with JSON mode."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = {
                "message": {"content": '{"result": true}'},
                "prompt_eval_count": 5,
                "eval_count": 10,
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            provider = OllamaProvider(model="llama3.1:70b")

            response = await provider.complete(
                [LLMMessage(role="user", content="Output JSON")],
                json_mode=True,
            )

            # Verify json_mode was passed
            call_kwargs = mock_client.chat.call_args[1]
            assert "format" in call_kwargs
            assert call_kwargs["format"] == "json"

    @pytest.mark.asyncio
    async def test_ollama_with_tools(self):
        """Test Ollama with tool definitions."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = {
                "message": {
                    "content": "Using tool",
                    "tool_calls": [
                        {
                            "function": {"name": "search", "arguments": {"q": "test"}},
                            "type": "function",
                        }
                    ],
                },
                "prompt_eval_count": 20,
                "eval_count": 10,
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            provider = OllamaProvider(model="qwen2.5:72b")

            tool_def = ToolDefinition(
                name="search",
                description="Search function",
                parameters={"type": "object"},
            )

            response = await provider.complete(
                [LLMMessage(role="user", content="Search for something")],
                tools=[tool_def],
            )

            assert response.tool_calls is not None
            assert response.tool_calls[0]["function"]["name"] == "search"

            # Verify tools were passed
            call_kwargs = mock_client.chat.call_args[1]
            assert "tools" in call_kwargs

    @pytest.mark.asyncio
    async def test_ollama_temperature_and_max_tokens(self):
        """Test temperature and max_tokens are passed correctly."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = {
                "message": {"content": "Response"},
                "prompt_eval_count": 5,
                "eval_count": 5,
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            provider = OllamaProvider(model="llama3.1:70b")

            await provider.complete(
                [LLMMessage(role="user", content="Test")],
                temperature=0.8,
                max_tokens=1000,
            )

            call_kwargs = mock_client.chat.call_args[1]
            assert call_kwargs["options"]["temperature"] == 0.8
            assert call_kwargs["options"]["num_predict"] == 1000

    @pytest.mark.asyncio
    async def test_ollama_custom_host(self):
        """Test Ollama with custom host."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            provider = OllamaProvider(
                model="qwen2.5:72b",
                host="http://gpu-server:11434",
            )

            # Verify custom host was passed
            mock_client_class.assert_called_once_with(host="http://gpu-server:11434")

    @pytest.mark.asyncio
    async def test_ollama_custom_options(self):
        """Test Ollama with custom options."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            mock_response = {
                "message": {"content": "Response"},
                "prompt_eval_count": 0,
                "eval_count": 0,
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            custom_options = {"num_gpu": 2, "num_ctx": 8192}
            provider = OllamaProvider(
                model="qwen2.5:72b",
                options=custom_options,
            )

            await provider.complete([LLMMessage(role="user", content="Test")])

            call_kwargs = mock_client.chat.call_args[1]
            # Custom options should be merged
            assert call_kwargs["options"]["num_gpu"] == 2
            assert call_kwargs["options"]["num_ctx"] == 8192


class TestProviderCommonBehavior:
    """Tests for common behavior across providers."""

    @pytest.mark.asyncio
    async def test_all_providers_return_llm_response(self):
        """Test that all providers return LLMResponse objects."""
        # This is a documentation test showing expected behavior

        # OpenAI
        with patch("anthropic.AsyncAnthropic"):
            mock_openai = AsyncMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "test"
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].finish_reason = "stop"
            mock_response.usage = None

            mock_openai.chat.completions.create = AsyncMock(return_value=mock_response)

            openai_provider = OpenAIProvider(mock_openai)
            openai_response = await openai_provider.complete(
                [LLMMessage(role="user", content="test")]
            )

            assert isinstance(openai_response, LLMResponse)

    @pytest.mark.asyncio
    async def test_provider_handles_missing_usage(self):
        """Test that providers handle missing usage information gracefully."""
        with patch("ollama.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Response without eval counts
            mock_response = {
                "message": {"content": "Response"},
                # Missing prompt_eval_count and eval_count
            }
            mock_client.chat = AsyncMock(return_value=mock_response)

            provider = OllamaProvider(model="llama3.1:70b")

            response = await provider.complete(
                [LLMMessage(role="user", content="Test")]
            )

            # Should not crash, usage should have defaults
            assert response.usage["prompt_tokens"] == 0
            assert response.usage["completion_tokens"] == 0
