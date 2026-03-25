"""Tests for protocols and value objects."""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from dynabots_core.protocols.agent import Agent, LegacyAgent
from dynabots_core.protocols.judge import Judge, ScoringJudge, Submission, Verdict
from dynabots_core.protocols.llm import LLMMessage, LLMProvider, LLMResponse, ToolDefinition
from dynabots_core.protocols.storage import (
    AuditStore,
    CacheStore,
    ExecutionStore,
    ReputationStore,
)
from dynabots_core.protocols.tool import Tool, tool_to_anthropic_format, tool_to_openai_format
from dynabots_core.value_objects.task_result import TaskResult


class TestAgentProtocol:
    """Tests for Agent protocol."""

    def test_agent_protocol_is_runtime_checkable(self):
        """Test that Agent protocol supports isinstance checks."""

        class SimpleAgent:
            @property
            def name(self) -> str:
                return "SimpleAgent"

            @property
            def capabilities(self) -> List[str]:
                return ["task_execution"]

            async def process_task(
                self,
                task_description: str,
                context: Dict[str, Any],
            ) -> TaskResult:
                result_data = {"completed": True}
                return TaskResult.success(
                    task_id=context["task_id"],
                    data=result_data,
                )

            async def health_check(self) -> bool:
                return True

        agent = SimpleAgent()
        assert isinstance(agent, Agent)

    def test_agent_with_domains(self):
        """Test agent with optional domains property."""

        class DomainAgent:
            @property
            def name(self) -> str:
                return "DomainAgent"

            @property
            def capabilities(self) -> List[str]:
                return ["analysis", "reporting"]

            @property
            def domains(self) -> List[str]:
                return ["data", "analytics"]

            async def process_task(
                self,
                task_description: str,
                context: Dict[str, Any],
            ) -> TaskResult:
                return TaskResult.success(
                    task_id=context["task_id"],
                    data={},
                )

            async def health_check(self) -> bool:
                return True

        agent = DomainAgent()
        assert isinstance(agent, Agent)
        assert agent.domains == ["data", "analytics"]

    def test_legacy_agent_protocol(self):
        """Test LegacyAgent protocol with execute_capability."""

        class LegacyImplementation:
            @property
            def name(self) -> str:
                return "LegacyAgent"

            @property
            def capabilities(self) -> List[str]:
                return ["fetch", "store"]

            async def execute_capability(
                self, capability: str, parameters: Dict[str, Any], context: Dict[str, Any]
            ) -> TaskResult:
                return TaskResult.success(task_id=context["task_id"], data={"executed": capability})

            async def health_check(self) -> bool:
                return True

        agent = LegacyImplementation()
        assert isinstance(agent, LegacyAgent)


class TestLLMMessageAndResponse:
    """Tests for LLMMessage and LLMResponse value objects."""

    def test_llm_message_creation(self):
        """Test creating LLMMessage."""
        msg = LLMMessage(role="user", content="Hello, world!")

        assert msg.role == "user"
        assert msg.content == "Hello, world!"
        assert msg.name is None
        assert msg.tool_calls is None
        assert msg.tool_call_id is None

    def test_llm_message_with_name(self):
        """Test LLMMessage with name."""
        msg = LLMMessage(role="assistant", content="Response", name="assistant_1")

        assert msg.role == "assistant"
        assert msg.name == "assistant_1"

    def test_llm_message_with_tool_calls(self):
        """Test LLMMessage with tool calls."""
        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "search", "arguments": '{"query": "test"}'},
            }
        ]
        msg = LLMMessage(role="assistant", content="Searching...", tool_calls=tool_calls)

        assert msg.tool_calls == tool_calls
        assert len(msg.tool_calls) == 1

    def test_llm_response_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(content="Test response")

        assert response.content == "Test response"
        assert response.usage is None
        assert response.model is None
        assert response.tool_calls is None
        assert response.finish_reason is None

    def test_llm_response_with_usage(self):
        """Test LLMResponse with token usage."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        response = LLMResponse(
            content="Response",
            usage=usage,
            model="gpt-4",
            finish_reason="stop",
        )

        assert response.usage == usage
        assert response.model == "gpt-4"
        assert response.finish_reason == "stop"

    def test_llm_response_with_tool_calls(self):
        """Test LLMResponse with tool calls."""
        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "fetch_data", "arguments": '{"id": "123"}'},
            }
        ]
        response = LLMResponse(
            content="",
            tool_calls=tool_calls,
            finish_reason="tool_calls",
        )

        assert response.tool_calls == tool_calls
        assert response.finish_reason == "tool_calls"

    def test_tool_definition(self):
        """Test ToolDefinition creation."""
        tool_def = ToolDefinition(
            name="search",
            description="Search the database",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        )

        assert tool_def.name == "search"
        assert tool_def.description == "Search the database"
        assert "query" in tool_def.parameters["properties"]

    def test_llm_provider_protocol(self):
        """Test that a class can satisfy LLMProvider protocol."""

        class MockLLMProvider:
            async def complete(
                self,
                messages: List[LLMMessage],
                temperature: float = 0.1,
                max_tokens: int = 2000,
                json_mode: bool = False,
                tools: List[ToolDefinition] = None,
            ) -> LLMResponse:
                return LLMResponse(content="Mock response")

        provider = MockLLMProvider()
        assert isinstance(provider, LLMProvider)


class TestToolProtocol:
    """Tests for Tool protocol."""

    def test_tool_protocol_implementation(self):
        """Test a class that satisfies Tool protocol."""

        class SearchTool:
            @property
            def name(self) -> str:
                return "search_database"

            @property
            def description(self) -> str:
                return "Search the database for records"

            @property
            def parameters_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "default": 10},
                    },
                    "required": ["query"],
                }

            async def execute(self, **kwargs: Any) -> Any:
                return {"results": []}

        tool = SearchTool()
        assert isinstance(tool, Tool)
        assert tool.name == "search_database"

    def test_tool_to_openai_format(self):
        """Test tool_to_openai_format() conversion."""

        class EmailTool:
            @property
            def name(self) -> str:
                return "send_email"

            @property
            def description(self) -> str:
                return "Send an email"

            @property
            def parameters_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                    },
                    "required": ["to", "subject"],
                }

            async def execute(self, **kwargs):
                return {"status": "sent"}

        tool = EmailTool()
        openai_format = tool_to_openai_format(tool)

        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "send_email"
        assert openai_format["function"]["description"] == "Send an email"
        assert "parameters" in openai_format["function"]

    def test_tool_to_anthropic_format(self):
        """Test tool_to_anthropic_format() conversion."""

        class DataFetchTool:
            @property
            def name(self) -> str:
                return "fetch_data"

            @property
            def description(self) -> str:
                return "Fetch data from API"

            @property
            def parameters_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {"endpoint": {"type": "string"}},
                    "required": ["endpoint"],
                }

            async def execute(self, **kwargs):
                return {"data": []}

        tool = DataFetchTool()
        anthropic_format = tool_to_anthropic_format(tool)

        assert anthropic_format["name"] == "fetch_data"
        assert anthropic_format["description"] == "Fetch data from API"
        assert "input_schema" in anthropic_format
        assert anthropic_format["input_schema"] == tool.parameters_schema

    def test_openai_vs_anthropic_format_differences(self):
        """Test differences between OpenAI and Anthropic tool formats."""

        class TestTool:
            @property
            def name(self) -> str:
                return "test_tool"

            @property
            def description(self) -> str:
                return "Test tool"

            @property
            def parameters_schema(self) -> Dict[str, Any]:
                return {"type": "object", "properties": {}}

            async def execute(self, **kwargs):
                return {}

        tool = TestTool()
        openai = tool_to_openai_format(tool)
        anthropic = tool_to_anthropic_format(tool)

        # OpenAI wraps in "type": "function"
        assert "type" in openai and openai["type"] == "function"
        assert "function" in openai

        # Anthropic doesn't wrap, parameters are in "input_schema"
        assert "input_schema" in anthropic
        assert "function" not in anthropic


class TestVerdictAndSubmission:
    """Tests for Verdict and Submission value objects."""

    def test_verdict_creation(self):
        """Test creating a Verdict."""
        verdict = Verdict(
            winner="AgentA",
            reasoning="AgentA produced more accurate results",
        )

        assert verdict.winner == "AgentA"
        assert verdict.reasoning == "AgentA produced more accurate results"
        assert verdict.scores == {}
        assert verdict.confidence == 1.0
        assert verdict.metadata == {}

    def test_verdict_with_scores(self):
        """Test Verdict with per-agent scores."""
        verdict = Verdict(
            winner="DataAgent",
            reasoning="Best overall performance",
            scores={"DataAgent": 0.95, "ReportAgent": 0.78},
            confidence=0.92,
        )

        assert verdict.scores == {"DataAgent": 0.95, "ReportAgent": 0.78}
        assert verdict.confidence == 0.92

    def test_verdict_is_tie(self):
        """Test is_tie property."""
        # Actual tie
        tie_verdict = Verdict(winner="", reasoning="Tie")
        assert tie_verdict.is_tie is True

        # Tie with lowercase
        tie_verdict2 = Verdict(winner="tie", reasoning="Tie")
        assert tie_verdict2.is_tie is True

        # Not a tie
        normal_verdict = Verdict(winner="AgentA", reasoning="Winner")
        assert normal_verdict.is_tie is False

    def test_verdict_to_dict(self):
        """Test Verdict.to_dict()."""
        verdict = Verdict(
            winner="Winner",
            reasoning="Best performance",
            scores={"A": 0.8, "B": 0.6},
            confidence=0.9,
            metadata={"method": "llm_eval"},
        )

        verdict_dict = verdict.to_dict()

        assert verdict_dict["winner"] == "Winner"
        assert verdict_dict["reasoning"] == "Best performance"
        assert verdict_dict["scores"] == {"A": 0.8, "B": 0.6}
        assert verdict_dict["confidence"] == 0.9
        assert verdict_dict["is_tie"] is False
        assert "timestamp" in verdict_dict

    def test_submission_creation(self):
        """Test creating a Submission."""
        result = TaskResult.success(task_id="t1", data={"value": 42})
        submission = Submission(
            agent="TestAgent",
            result=result,
        )

        assert submission.agent == "TestAgent"
        assert submission.result == result
        assert submission.latency_ms is None
        assert submission.cost is None

    def test_submission_with_metrics(self):
        """Test Submission with latency and cost."""
        submission = Submission(
            agent="Agent1",
            result={"output": "data"},
            latency_ms=150,
            cost=0.02,
            metadata={"model": "gpt-4"},
        )

        assert submission.latency_ms == 150
        assert submission.cost == 0.02
        assert submission.metadata == {"model": "gpt-4"}

    def test_submission_to_dict(self):
        """Test Submission.to_dict()."""
        result = TaskResult.success(task_id="t", data={"value": 10})
        submission = Submission(
            agent="TestAgent",
            result=result,
            latency_ms=200,
            cost=0.01,
            metadata={"attempt": 1},
        )

        sub_dict = submission.to_dict()

        assert sub_dict["agent"] == "TestAgent"
        assert "result" in sub_dict
        assert sub_dict["latency_ms"] == 200
        assert sub_dict["cost"] == 0.01
        assert sub_dict["metadata"]["attempt"] == 1

    def test_submission_to_dict_with_taskresult(self):
        """Test that to_dict() calls to_dict() on TaskResult."""
        result = TaskResult.success(task_id="t1", data={"count": 5})
        submission = Submission(agent="Agent", result=result)

        sub_dict = submission.to_dict()

        # Result should be converted via to_dict()
        assert isinstance(sub_dict["result"], dict)
        assert sub_dict["result"]["task_id"] == "t1"


class TestJudgeProtocol:
    """Tests for Judge protocol."""

    def test_judge_protocol_implementation(self):
        """Test a class that satisfies Judge protocol."""

        class SimpleJudge:
            async def evaluate(self, task: str, submissions: List[Submission]) -> Verdict:
                winner = submissions[0].agent if submissions else "unknown"
                return Verdict(
                    winner=winner,
                    reasoning="First agent wins",
                    scores={s.agent: 0.5 for s in submissions},
                )

        judge = SimpleJudge()
        assert isinstance(judge, Judge)

    def test_scoring_judge_protocol(self):
        """Test a class that satisfies ScoringJudge protocol."""

        class MetricsJudge:
            async def score(self, task: str, submission: Submission) -> float:
                # Simple scoring based on latency
                if submission.latency_ms is None:
                    return 0.5
                return 1.0 - (submission.latency_ms / 10000)

            async def evaluate(self, task: str, submissions: List[Submission]) -> Verdict:
                scores = {}
                for sub in submissions:
                    scores[sub.agent] = await self.score(task, sub)

                winner = max(scores, key=scores.get)
                return Verdict(
                    winner=winner,
                    reasoning="Highest score wins",
                    scores=scores,
                )

        judge = MetricsJudge()
        assert isinstance(judge, ScoringJudge)
        assert isinstance(judge, Judge)


class TestStorageProtocols:
    """Tests for storage protocols."""

    def test_execution_store_protocol(self):
        """Test a class that satisfies ExecutionStore protocol."""

        class InMemoryExecutionStore:
            def __init__(self):
                self.workflows = {}

            async def save_workflow(self, workflow_data: Dict[str, Any]) -> bool:
                self.workflows[workflow_data["id"]] = workflow_data
                return True

            async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
                return self.workflows.get(workflow_id)

            async def list_workflows(self, limit: int = 50, **filters) -> List[Dict[str, Any]]:
                return list(self.workflows.values())[:limit]

        store = InMemoryExecutionStore()
        assert isinstance(store, ExecutionStore)

    def test_audit_store_protocol(self):
        """Test a class that satisfies AuditStore protocol."""

        class InMemoryAuditStore:
            def __init__(self):
                self.logs = []

            async def log_workflow(self, workflow_id: str, data: Dict[str, Any]) -> bool:
                self.logs.append({"type": "workflow", "workflow_id": workflow_id, "data": data})
                return True

            async def log_task(
                self,
                workflow_id: str,
                task_id: str,
                data: Dict[str, Any],
            ) -> bool:
                log_entry = {
                    "type": "task",
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "data": data,
                }
                self.logs.append(log_entry)
                return True

            async def log_error(
                self,
                workflow_id: str,
                error_type: str,
                message: str,
            ) -> bool:
                log_entry = {
                    "type": "error",
                    "workflow_id": workflow_id,
                    "error_type": error_type,
                    "message": message,
                }
                self.logs.append(log_entry)
                return True

        store = InMemoryAuditStore()
        assert isinstance(store, AuditStore)

    def test_cache_store_protocol(self):
        """Test a class that satisfies CacheStore protocol."""

        class InMemoryCacheStore:
            def __init__(self):
                self.cache = {}

            async def get(self, key: str) -> Dict[str, Any]:
                return self.cache.get(key)

            async def set(self, key: str, value: Dict[str, Any]) -> bool:
                self.cache[key] = value
                return True

            async def delete(self, key: str) -> bool:
                if key in self.cache:
                    del self.cache[key]
                    return True
                return False

        store = InMemoryCacheStore()
        assert isinstance(store, CacheStore)

    def test_reputation_store_protocol(self):
        """Test a class that satisfies ReputationStore protocol."""

        class InMemoryReputationStore:
            def __init__(self):
                self.scores = {}

            async def get_reputation(self, agent_name: str, domain: str) -> float:
                return self.scores.get((agent_name, domain), 0.5)

            async def update_reputation(self, agent_name: str, domain: str, delta: float) -> bool:
                key = (agent_name, domain)
                self.scores[key] = self.scores.get(key, 0.5) + delta
                return True

            async def get_leaderboard(self, domain: str, limit: int = 10) -> List[Dict[str, Any]]:
                domain_scores = [(k[0], v) for k, v in self.scores.items() if k[1] == domain]
                sorted_scores = sorted(domain_scores, key=lambda x: x[1], reverse=True)
                return [{"agent": name, "score": score} for name, score in sorted_scores[:limit]]

        store = InMemoryReputationStore()
        assert isinstance(store, ReputationStore)


class TestProtocolCombinations:
    """Tests for using multiple protocols together."""

    def test_agent_with_judge(self):
        """Test an agent being evaluated by a judge."""

        class TestAgent:
            @property
            def name(self) -> str:
                return "TestAgent"

            @property
            def capabilities(self) -> List[str]:
                return ["process"]

            async def process_task(self, task: str, context: Dict[str, Any]) -> TaskResult:
                return TaskResult.success(task_id=context["task_id"], data={"result": "success"})

            async def health_check(self) -> bool:
                return True

        class TestJudge:
            async def evaluate(self, task: str, submissions: List[Submission]) -> Verdict:
                return Verdict(
                    winner=submissions[0].agent if submissions else "none",
                    reasoning="Test verdict",
                )

        agent = TestAgent()
        judge = TestJudge()

        assert isinstance(agent, Agent)
        assert isinstance(judge, Judge)

    def test_llm_with_tools(self):
        """Test LLM provider with tools."""

        class SimpleTool:
            @property
            def name(self) -> str:
                return "simple_tool"

            @property
            def description(self) -> str:
                return "A simple tool"

            @property
            def parameters_schema(self) -> Dict[str, Any]:
                return {"type": "object"}

            async def execute(self, **kwargs):
                return {"executed": True}

        class SimpleLLM:
            async def complete(
                self,
                messages: List[LLMMessage],
                temperature: float = 0.1,
                max_tokens: int = 2000,
                json_mode: bool = False,
                tools: List[ToolDefinition] = None,
            ) -> LLMResponse:
                return LLMResponse(content="Response with tools")

        tool = SimpleTool()
        llm = SimpleLLM()

        assert isinstance(tool, Tool)
        assert isinstance(llm, LLMProvider)
