"""
Orc!! Arena Example

Demonstrates brutalist hierarchy orchestration where agents
compete for leadership through trials.

Run with:
    python orc_arena_example.py
"""

import asyncio
from typing import Any, Dict, List

from dynabots_orc import Arena, LLMJudge, ReputationBased

from dynabots_core import TaskResult
from dynabots_core.providers import OllamaProvider

# Define competing agents

class DataAgent:
    """Agent specializing in data operations."""

    @property
    def name(self) -> str:
        return "DataAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["fetch_data", "query_database", "transform_data"]

    @property
    def domains(self) -> List[str]:
        return ["data", "analytics", "database"]

    # Use reputation-based challenge strategy
    challenge_strategy = ReputationBased(threshold=0.05)

    async def process_task(self, task: str, context: Dict[str, Any]) -> TaskResult:
        """Process a data-related task."""
        print(f"  [DataAgent] Processing: {task[:50]}...")

        # Simulate work
        await asyncio.sleep(0.5)

        # Simulate result
        result = {
            "source": "database",
            "records": 42,
            "summary": f"DataAgent processed: {task}",
        }

        return TaskResult.success(
            task_id=context.get("task_id", "unknown"),
            data=result,
            metadata={"agent": self.name},
        )

    async def health_check(self) -> bool:
        return True


class AnalyticsAgent:
    """Agent specializing in analytics and insights."""

    @property
    def name(self) -> str:
        return "AnalyticsAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["analyze", "generate_insights", "create_visualizations"]

    @property
    def domains(self) -> List[str]:
        return ["analytics", "data", "reporting"]  # Overlaps with DataAgent!

    challenge_strategy = ReputationBased(threshold=0.0)  # More aggressive

    async def process_task(self, task: str, context: Dict[str, Any]) -> TaskResult:
        """Process an analytics task."""
        print(f"  [AnalyticsAgent] Processing: {task[:50]}...")

        await asyncio.sleep(0.4)  # Slightly faster

        result = {
            "source": "analytics_engine",
            "insights": ["trend_up", "anomaly_detected"],
            "summary": f"AnalyticsAgent analyzed: {task}",
        }

        return TaskResult.success(
            task_id=context.get("task_id", "unknown"),
            data=result,
            metadata={"agent": self.name},
        )

    async def health_check(self) -> bool:
        return True


class ReportAgent:
    """Agent specializing in report generation."""

    @property
    def name(self) -> str:
        return "ReportAgent"

    @property
    def capabilities(self) -> List[str]:
        return ["generate_report", "summarize", "export_pdf"]

    @property
    def domains(self) -> List[str]:
        return ["reporting", "documents"]  # Minimal overlap

    async def process_task(self, task: str, context: Dict[str, Any]) -> TaskResult:
        """Generate a report."""
        print(f"  [ReportAgent] Processing: {task[:50]}...")

        await asyncio.sleep(0.6)

        result = {
            "report_type": "summary",
            "pages": 5,
            "summary": f"ReportAgent created report for: {task}",
        }

        return TaskResult.success(
            task_id=context.get("task_id", "unknown"),
            data=result,
            metadata={"agent": self.name},
        )

    async def health_check(self) -> bool:
        return True


async def main():
    print("=" * 60)
    print("ORC!! ARENA - Brutalist Hierarchy Orchestration")
    print("=" * 60)
    print()

    # Create LLM provider (use local Ollama)
    # For testing without Ollama, we'll create a mock judge
    try:
        llm = OllamaProvider(model="qwen2.5:7b")  # Use smaller model for demo
        judge = LLMJudge(llm)
        print("Using Ollama LLM Judge")
    except Exception as e:
        print(f"Ollama not available ({e}), using mock judge")
        # Mock judge for testing
        from dynabots_core import Verdict
        from dynabots_core.protocols.judge import Submission

        class MockJudge:
            async def evaluate(self, task: str, submissions: List[Submission]) -> Verdict:
                # Simple mock: prefer faster agent
                winner = min(submissions, key=lambda s: s.latency_ms or 9999)
                return Verdict(
                    winner=winner.agent,
                    reasoning="Faster execution wins",
                    scores={s.agent: 0.5 for s in submissions},
                )

        judge = MockJudge()

    # Create arena with agents
    def on_challenge_handler(warlord, challenger, domain):
        print(f"\n⚔️  CHALLENGE: {challenger} challenges {warlord} for '{domain}' domain!")

    def on_succession_handler(old_warlord, new_warlord, domain):
        print(f"👑 SUCCESSION: {new_warlord} defeats {old_warlord}, now rules '{domain}'!")

    arena = Arena(
        agents=[DataAgent(), AnalyticsAgent(), ReportAgent()],
        judge=judge,
        on_challenge=on_challenge_handler,
        on_succession=on_succession_handler,
    )

    print("\nInitial Warlords:")
    for domain in ["data", "analytics", "reporting"]:
        warlord = arena.get_warlord(domain)
        print(f"  {domain}: {warlord}")

    print("\n" + "-" * 60)
    print("Processing tasks (may trigger trials)...")
    print("-" * 60)

    # Process some tasks
    tasks = [
        ("Analyze Q4 sales data", "analytics"),
        ("Fetch customer records from database", "data"),
        ("Generate monthly summary report", "reporting"),
        ("Query revenue trends for 2024", "data"),
        ("Create visualization of user growth", "analytics"),
    ]

    for task, domain in tasks:
        print(f"\n📋 Task: {task}")
        print(f"   Domain: {domain}")

        result = await arena.process(task, domain=domain)

        print(f"   Winner: {result.winner}")
        print(f"   Challenged: {result.was_challenged}")
        if result.verdict:
            print(f"   Verdict: {result.verdict.reasoning[:100]}...")

    print("\n" + "=" * 60)
    print("FINAL STANDINGS")
    print("=" * 60)

    for domain in ["data", "analytics", "reporting"]:
        print(f"\n{domain.upper()} Domain:")
        leaderboard = arena.get_leaderboard(domain, limit=3)
        for i, entry in enumerate(leaderboard, 1):
            warlord = "👑" if entry["is_warlord"] else "  "
            print(
                f"  {warlord} {i}. {entry['agent']}: "
                f"rep={entry['reputation']:.2f}, "
                f"W={entry['wins']}, L={entry['losses']}"
            )

    print("\n" + "=" * 60)
    print("Trial History:")
    print("=" * 60)
    for trial in arena.get_trial_history():
        if trial.was_challenged:
            print(f"  {trial.domain}: {trial.winner} won")


if __name__ == "__main__":
    asyncio.run(main())
