"""
Arena - The heart of Orc!! orchestration.

The Arena manages agent competition, trials, and leadership succession.
"""

from dynabots_orc.arena.arena import Arena, ArenaConfig
from dynabots_orc.arena.trial import TrialResult, Trial

__all__ = ["Arena", "ArenaConfig", "TrialResult", "Trial"]
