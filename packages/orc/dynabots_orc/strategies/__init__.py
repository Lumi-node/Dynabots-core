"""
Challenge strategies for Orc!!

Strategies determine when an agent should challenge the current Warlord.
"""

from dynabots_orc.strategies.base import ChallengeStrategy
from dynabots_orc.strategies.always import AlwaysChallenge
from dynabots_orc.strategies.reputation import ReputationBased
from dynabots_orc.strategies.cooldown import CooldownStrategy
from dynabots_orc.strategies.specialist import SpecialistStrategy

__all__ = [
    "ChallengeStrategy",
    "AlwaysChallenge",
    "ReputationBased",
    "CooldownStrategy",
    "SpecialistStrategy",
]
