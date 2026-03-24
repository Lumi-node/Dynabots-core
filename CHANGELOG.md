# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-23

### Added

#### dynabots-core
- Agent, LLMProvider, Judge, Tool protocols with `@runtime_checkable` support
- Storage protocols: ExecutionStore, AuditStore, CacheStore, ReputationStore
- Swarm protocols: SwarmParticipant, SwarmMessageBus
- LLM providers: OpenAI, Anthropic, Ollama with unified interface
- TaskResult value object with factory methods and serialization
- Verdict and Submission dataclasses for judge evaluations
- Tool format converters for OpenAI and Anthropic schemas
- PEP 561 py.typed marker for type checker support

#### dynabots-orc
- Arena orchestration with warlord/challenger/trial system
- ArenaConfig for challenge probability, cooldowns, rotation limits
- Trial execution with parallel and sequential modes
- LLMJudge for LLM-based evaluation of agent submissions
- MetricsJudge for accuracy/latency/cost scoring
- ConsensusJudge for multi-judge voting
- Challenge strategies: AlwaysChallenge, ReputationBased, CooldownStrategy, SpecialistStrategy
- Reputation tracking with domain-scoped scores
- Hook system for challenge, succession, and trial events
- Dynamic agent registration and unregistration
