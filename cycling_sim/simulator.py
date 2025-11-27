"""Monte-Carlo runner for repeated race simulations."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List

from .physiology import Physiology
from .rider import Rider
from .race import Race
from .route import Route, RouteSegment


@dataclass
class SimulationConfig:
    races: int = 100
    dt: float = 0.2
    draft: bool = True


class Simulator:
    """Generate riders, run races, and summarize winners."""

    def __init__(self, route: Route, config: SimulationConfig):
        self.route = route
        self.config = config

    def random_rider(self, idx: int) -> Rider:
        """Create a rider with randomized physiological traits."""

        mass = random.uniform(65, 80)
        cp = random.uniform(280, 360)
        w_prime = random.uniform(15000, 25000)  # joules
        cda = random.uniform(0.25, 0.35)
        crr = random.uniform(0.003, 0.005)
        sprint = random.uniform(900, 1300)

        phys = Physiology(critical_power=cp, w_prime=w_prime, sprint_power=sprint)
        return Rider(
            name=f"Rider_{idx}",
            mass=mass,
            cda=cda,
            crr=crr,
            physiology=phys,
        )

    def run_race(self, riders: List[Rider]) -> str:
        race = Race(riders, self.route, dt=self.config.dt)
        result = race.run()
        return result.order[0]

    def run(self) -> dict[str, float]:
        """Run many races and return win percentages per rider archetype."""

        win_counter: Counter[str] = Counter()
        trait_logs: defaultdict[str, list[float]] = defaultdict(list)

        for i in range(self.config.races):
            riders = [self.random_rider(idx) for idx in range(5)]
            winner = self.run_race(riders)
            win_counter[winner] += 1

            # Log winner traits for quick insight.
            winning_rider = next(r for r in riders if r.name == winner)
            trait_logs["mass"].append(winning_rider.mass)
            trait_logs["cp"].append(winning_rider.physiology.critical_power)
            trait_logs["w_prime"].append(winning_rider.physiology.w_prime)
            trait_logs["cda"].append(winning_rider.cda)

        wins = {k: v / self.config.races for k, v in win_counter.items()}
        summary = {"wins": wins, "traits": trait_logs}
        return summary


def default_route() -> Route:
    """Create a simple mixed-terrain route for examples."""

    segments = [
        RouteSegment(length=3000.0, gradient=0.0),
        RouteSegment(length=2000.0, gradient=0.03),
        RouteSegment(length=3000.0, gradient=-0.01),
        RouteSegment(length=2000.0, gradient=0.05),
        RouteSegment(length=2000.0, gradient=0.0),
    ]
    return Route(segments)


__all__ = ["Simulator", "SimulationConfig", "default_route"]
