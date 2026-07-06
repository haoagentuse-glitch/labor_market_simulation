"""可插拔機制：learning、frontier_ceiling（未來：demand 等）。"""

from labor_sim.mechanisms.base import Mechanism
from labor_sim.mechanisms.learning import LearningMechanism
from labor_sim.mechanisms.frontier_ceiling import FrontierCeilingMechanism

__all__ = ["Mechanism", "LearningMechanism", "FrontierCeilingMechanism"]
