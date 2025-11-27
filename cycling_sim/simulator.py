"""Monte-Carlo runner for repeated race simulations."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List

from .physiology import Physiology
from .rider import Rider
from .race import Race, RaceResult
from .route import Route, RouteSegment


@dataclass
class SimulationConfig:
    races: int = 100
    dt: float = 0.2
    draft: bool = True
    progress: bool = False
    progress_interval: int = 100


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

    def run_race(self, riders: List[Rider]) -> RaceResult:
        race = Race(riders, self.route, dt=self.config.dt)
        return race.run()

    @staticmethod
    def _classify_winner_style(cp: float, mass: float, cda: float, sprint: float) -> str:
        """Roughly categorize a winner by terrain style.

        The scores are normalized to keep magnitudes comparable, highlighting whether a
        rider is winning thanks to climbing power (w/kg), aerodynamic efficiency, or a
        finishing kick.
        """

        cp_per_kg = cp / mass
        aero_score = cp / cda
        style_scores = {
            "climb": cp_per_kg / 6.0,  # typical winners fall between 4-6 w/kg
            "flat": aero_score / 1400.0,
            "sprint": sprint / 1300.0,
        }
        return max(style_scores, key=style_scores.get)

    def run(self) -> dict[str, float]:
        """Run many races and return win percentages per rider archetype."""

        win_counter: Counter[str] = Counter()
        terrain_styles: Counter[str] = Counter()
        trait_logs: defaultdict[str, list[float]] = defaultdict(list)
        finish_times: list[float] = []

        for i in range(self.config.races):
            riders = [self.random_rider(idx) for idx in range(5)]
            result = self.run_race(riders)
            winner = result.order[0]
            win_counter[winner] += 1

            # Log winner traits for quick insight.
            winning_rider = next(r for r in riders if r.name == winner)
            finish_times.append(result.finish_times[winner])
            trait_logs["mass"].append(winning_rider.mass)
            trait_logs["cp"].append(winning_rider.physiology.critical_power)
            trait_logs["w_prime"].append(winning_rider.physiology.w_prime)
            trait_logs["cda"].append(winning_rider.cda)
            trait_logs["cp_per_kg"].append(
                winning_rider.physiology.critical_power / winning_rider.mass
            )
            trait_logs["aero_score"].append(
                winning_rider.physiology.critical_power / winning_rider.cda
            )
            trait_logs["sprint"].append(winning_rider.physiology.sprint_power)

            style = self._classify_winner_style(
                cp=winning_rider.physiology.critical_power,
                mass=winning_rider.mass,
                cda=winning_rider.cda,
                sprint=winning_rider.physiology.sprint_power,
            )
            terrain_styles[style] += 1

            if self.config.progress and (i + 1) % self.config.progress_interval == 0:
                completed = i + 1
                print(
                    f"  Progress: {completed}/{self.config.races} races completed",
                    flush=True,
                )

        wins = {k: v / self.config.races for k, v in win_counter.items()}
        style_fraction = {
            k: v / self.config.races for k, v in sorted(terrain_styles.items())
        }
        avg_finish_time = sum(finish_times) / len(finish_times) if finish_times else 0.0
        summary = {
            "wins": wins,
            "traits": trait_logs,
            "route_profile": self.route.terrain_profile(),
            "route_total_km": self.route.total_length / 1000.0,
            "style_fraction": style_fraction,
            "avg_finish_time": avg_finish_time,
            "avg_winner_speed_kph": (self.route.total_length / avg_finish_time)
            * 3.6
            if avg_finish_time
            else 0.0,
        }
        return summary


def default_route() -> Route:
    """Create a simple mixed-terrain route for examples."""

    segments = [
        RouteSegment(length=6000.0, gradient=0.01),
        RouteSegment(length=4000.0, gradient=0.04),
        RouteSegment(length=6000.0, gradient=-0.02),
        RouteSegment(length=5000.0, gradient=0.06),
        RouteSegment(length=4000.0, gradient=0.0),
    ]
    return Route(segments)


__all__ = ["Simulator", "SimulationConfig", "default_route"]
