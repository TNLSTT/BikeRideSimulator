"""Physiology model for simplified rider energy management."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Physiology:
    """Tracks rider energetic state and fatigue."""

    critical_power: float  # CP in watts
    w_prime: float  # Anaerobic work capacity in joules
    fatigue_kj: float = 800.0  # kJ at which fatigue significantly reduces CP
    fatigue_penalty: float = 0.15  # Fractional CP drop at fatigue_kj
    sprint_power: float = 1100.0

    w_balance: float = field(init=False)
    total_kj: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.w_balance = self.w_prime

    def fatigue_adjusted_cp(self) -> float:
        """Return CP adjusted for accumulated work."""

        fatigue_ratio = min(self.total_kj / self.fatigue_kj, 1.0)
        cp_drop = self.fatigue_penalty * fatigue_ratio
        adjusted_cp = self.critical_power * max(0.0, 1.0 - cp_drop)
        return adjusted_cp

    def update(self, power: float, dt: float) -> None:
        """Update energetic state based on current power output."""

        cp = self.fatigue_adjusted_cp()
        work_j = power * dt
        self.total_kj += work_j / 1000.0

        if power > cp:
            # Above CP draws from W′. Clamp at zero.
            depletion = (power - cp) * dt
            self.w_balance = max(0.0, self.w_balance - depletion)
        else:
            # Below CP allows exponential recovery. Use a simple linear proxy
            # controlled by how far below CP we are.
            recovery_rate = (cp - power) * dt * 0.25
            self.w_balance = min(self.w_prime, self.w_balance + recovery_rate)

    def available_power(self) -> float:
        """Return a rough ceiling on sustainable power given current state."""

        cp = self.fatigue_adjusted_cp()
        # If W′ is nearly depleted, discourage efforts far over CP.
        if self.w_balance < 0.2 * self.w_prime:
            return cp * 1.05
        return cp * 1.4

    def is_cooked(self) -> bool:
        """Determine if the rider is exhausted (no W′ and low CP)."""

        return self.w_balance <= 1.0 and self.fatigue_adjusted_cp() < 0.8 * self.critical_power
