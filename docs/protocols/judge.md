# Judge Protocol

Evaluates and compares agent submissions in competitive orchestration.

---

## Protocol Definition

::: dynabots_core.protocols.judge.Judge

::: dynabots_core.protocols.judge.Verdict

::: dynabots_core.protocols.judge.Submission

::: dynabots_core.protocols.judge.ScoringJudge

---

## Simple Implementation

```python
from typing import Any, Dict, List
from dynabots_core import Judge, Verdict
from dynabots_core.protocols.judge import Submission

class FastestWinsJudge:
    """Judge that awards the fastest submission."""

    async def evaluate(
        self,
        task: str,
        submissions: List[Submission],
    ) -> Verdict:
        """Winner is the fastest agent."""
        if not submissions:
            return Verdict(
                winner="none",
                reasoning="No submissions to evaluate"
            )

        # Sort by latency
        fastest = min(submissions, key=lambda s: s.latency_ms or float('inf'))

        return Verdict(
            winner=fastest.agent,
            reasoning=f"{fastest.agent} executed fastest ({fastest.latency_ms}ms)",
            scores={
                s.agent: 1.0 if s.agent == fastest.agent else 0.0
                for s in submissions
            },
            confidence=1.0,
        )
```

---

## LLM-Based Judge

Use an LLM to evaluate submissions:

```python
from dynabots_core import Judge, Verdict, LLMMessage
from dynabots_core.protocols.judge import Submission
from dynabots_core.providers import OllamaProvider
from typing import List

class LLMJudge:
    """Judge using an LLM to evaluate submissions."""

    def __init__(self, llm):
        self.llm = llm

    async def evaluate(
        self,
        task: str,
        submissions: List[Submission],
    ) -> Verdict:
        """Use LLM to evaluate submissions."""
        # Format submissions for LLM
        submissions_text = "\n\n".join([
            f"Submission from {s.agent}:\n{s.result}"
            for s in submissions
        ])

        prompt = f"""You are evaluating agent submissions for a task.

Task: {task}

Submissions:
{submissions_text}

Evaluate each submission on:
- Accuracy and correctness
- Completeness of response
- Clarity and helpfulness
- Efficiency (consider latency if provided)

Provide your evaluation as JSON:
{{
    "winner": "name of winning agent",
    "reasoning": "brief explanation",
    "scores": {{"agent1": 0.9, "agent2": 0.7}}
}}"""

        response = await self.llm.complete([
            LLMMessage(role="user", content=prompt)
        ])

        # Parse LLM response
        import json
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: pick first
            result = {
                "winner": submissions[0].agent if submissions else "unknown",
                "reasoning": "Could not parse LLM response",
                "scores": {}
            }

        return Verdict(
            winner=result["winner"],
            reasoning=result["reasoning"],
            scores=result.get("scores", {}),
            confidence=0.8,  # LLM judges have inherent uncertainty
        )
```

---

## Metrics-Based Judge

Score submissions using objective metrics:

```python
from dynabots_core import Judge, Verdict
from dynabots_core.protocols.judge import Submission
from typing import List

class MetricsJudge:
    """Judge based on objective metrics."""

    async def evaluate(
        self,
        task: str,
        submissions: List[Submission],
    ) -> Verdict:
        """Score submissions using metrics."""
        scores = {}

        for submission in submissions:
            score = 0.0

            # Accuracy (simulated check)
            if self._is_correct(submission.result):
                score += 50

            # Speed bonus (faster = better)
            if submission.latency_ms and submission.latency_ms < 1000:
                speed_bonus = (1000 - submission.latency_ms) / 1000 * 30
                score += speed_bonus

            # Cost efficiency (lower cost = better)
            if submission.cost and submission.cost < 0.1:
                cost_bonus = (0.1 - submission.cost) / 0.1 * 20
                score += cost_bonus

            scores[submission.agent] = score

        # Determine winner
        winner = max(scores, key=scores.get) if scores else "unknown"
        max_score = scores.get(winner, 0) if scores else 0

        return Verdict(
            winner=winner,
            reasoning=f"Highest composite score: {max_score:.1f}",
            scores={k: round(v, 1) for k, v in scores.items()},
            confidence=1.0,  # Metrics are deterministic
        )

    def _is_correct(self, result) -> bool:
        """Check if result is correct (domain-specific)."""
        # Implement your correctness check
        return True
```

---

## Consensus Judge

Multiple judges vote:

```python
from dynabots_core import Judge, Verdict
from dynabots_core.protocols.judge import Submission
from typing import List
from collections import Counter

class ConsensusJudge:
    """Multiple judges vote on winner."""

    def __init__(self, judges: List[Judge]):
        self.judges = judges

    async def evaluate(
        self,
        task: str,
        submissions: List[Submission],
    ) -> Verdict:
        """Collect verdicts from all judges."""
        verdicts = []

        for judge in self.judges:
            verdict = await judge.evaluate(task, submissions)
            verdicts.append(verdict)

        # Consensus: most common winner
        winners = [v.winner for v in verdicts]
        winner = Counter(winners).most_common(1)[0][0]

        # Average scores
        avg_scores = {}
        for agent in {s.agent for s in submissions}:
            agent_scores = [
                v.scores.get(agent, 0)
                for v in verdicts
                if v.scores
            ]
            if agent_scores:
                avg_scores[agent] = sum(agent_scores) / len(agent_scores)

        # Confidence based on consensus
        confidence = winners.count(winner) / len(verdicts) if verdicts else 0

        return Verdict(
            winner=winner,
            reasoning=f"{len(verdicts)} judges voted; {winner} wins ({confidence:.1%} consensus)",
            scores=avg_scores,
            confidence=confidence,
        )
```

---

## Tie Handling

What if submissions are equivalent?

```python
class TieAwareJudge:
    async def evaluate(self, task: str, submissions: List[Submission]) -> Verdict:
        # ... evaluation logic ...

        if performance_is_equal:
            return Verdict(
                winner="tie",  # Signal a tie
                reasoning="Both submissions equal in all metrics",
                scores={s.agent: 0.5 for s in submissions},
                confidence=1.0,
            )
```

In orchestration frameworks, a tie usually means the current leader stays (no succession).

---

## Verdict Properties

The result of evaluation:

```python
verdict = await judge.evaluate(task, submissions)

# Core
print(verdict.winner)       # Winning agent name
print(verdict.reasoning)    # Why they won

# Metrics
print(verdict.scores)       # {"Agent1": 0.9, "Agent2": 0.7}
print(verdict.confidence)   # 0.0 to 1.0

# Metadata
print(verdict.metadata)     # Custom data
print(verdict.timestamp)    # When rendered

# Convenience
print(verdict.is_tie)       # Check if tie
```

---

## Submission Properties

What judges receive:

```python
submission = Submission(
    agent="DataAgent",
    result=TaskResult.success(...),
    latency_ms=250,           # How long it took
    cost=0.01,                # API cost
    metadata={"accuracy": 0.95}  # Custom data
)

print(submission.agent)       # Agent name
print(submission.result)      # TaskResult
print(submission.latency_ms)  # Execution time
print(submission.cost)        # Financial cost
print(submission.metadata)    # Additional data
```

---

## Domain-Specific Judges

Create judges for your domain:

```python
from dynabots_core import Judge, Verdict
from dynabots_core.protocols.judge import Submission
from typing import List

class CodeQualityJudge:
    """Judge code submissions on quality."""

    async def evaluate(
        self,
        task: str,
        submissions: List[Submission],
    ) -> Verdict:
        """Evaluate code quality."""
        scores = {}

        for submission in submissions:
            code = submission.result.data.get("code", "")

            quality = 0.0

            # Style
            if self._check_style(code):
                quality += 20

            # Tests
            if self._has_tests(code):
                quality += 30

            # Performance
            if self._is_performant(code):
                quality += 20

            # Documentation
            if self._has_docs(code):
                quality += 20

            # Correctness (if submitting results)
            if self._passes_tests(code):
                quality += 10

            scores[submission.agent] = quality

        winner = max(scores, key=scores.get) if scores else "unknown"

        return Verdict(
            winner=winner,
            reasoning=f"{winner} has best code quality ({scores.get(winner, 0):.0f}/100)",
            scores=scores,
            confidence=0.9,
        )

    def _check_style(self, code: str) -> bool:
        # Check PEP 8, etc.
        return True

    def _has_tests(self, code: str) -> bool:
        return "def test_" in code

    def _is_performant(self, code: str) -> bool:
        # Check time complexity, etc.
        return True

    def _has_docs(self, code: str) -> bool:
        return '"""' in code

    def _passes_tests(self, code: str) -> bool:
        # Run tests
        return True
```

---

## Best Practices

1. **Clear reasoning**: Always provide detailed reasoning. Used for learning and debugging.
2. **Consistent scoring**: Use 0.0 to 1.0 for scores. Makes comparison easier.
3. **Confidence**: Include confidence in your verdict. Uncertainty helps orchestration.
4. **Metadata**: Attach evaluation details in metadata for analysis.
5. **Determinism**: For testing, judges should be deterministic (or document randomness).

---

## See Also

- [Core Concepts: Judge](../getting-started/concepts.md#judge)
- [Agent Protocol](agent.md)
- [ORC Orchestration](../ecosystem/orc.md)
