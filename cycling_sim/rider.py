"""Rider model tying together physiology and behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .physiology import Physiology


@dataclass
class Rider:
    name: str
    mass: float  # kg including bike
    cda: float  # m^2
    crr: float  # rolling resistance coefficient
    physiology: Physiology

    position: float = 0.0  # meters along the course
    velocity: float = 0.0  # m/s
    finished: bool = False
    finish_time: float | None = None

    # Extra space to store custom strategy parameters.
    strategy: Dict[str, Any] = field(default_factory=dict)

    def choose_power(self, state: dict[str, Any]) -> float:
        """Placeholder AI deciding power for the next step.

        The logic here is intentionally simple but uses a few realistic heuristics:
        - Stay in the draft if possible.
        - Close gaps > 5 m by pushing harder when W′ is healthy.
        - Avoid surges above CP when deeply fatigued.
        """

        phys = self.physiology
        cp = phys.fatigue_adjusted_cp()
        max_power = min(phys.available_power(), phys.sprint_power)

        gap = state.get("gap", 0.0)
        at_front = state.get("at_front", False)

        # If nearly cooked, ride conservatively near CP.
        if phys.w_balance < 0.2 * phys.w_prime:
            return cp * 0.95

        # If off the back, increase power to chase back.
        if gap > 5.0 and not at_front:
            return min(max_power, cp * 1.3)

        # If comfortably drafting, ride a bit under CP to save energy.
        if not at_front and gap < 2.0:
            return cp * 0.9

        # Otherwise, ride at or slightly above CP when at the front.
        if at_front:
            return min(max_power, cp * 1.1)

        return cp
