"""Race loop tying together riders, physics, and physiology."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .physics import compute_next_speed
from .rider import Rider
from .route import Route


def compute_draft_factor(gap: float) -> float:
    """Return aerodynamic multiplier based on rider gap."""

    if gap < 2.0:
        return 0.7
    if gap < 5.0:
        return 0.85
    return 1.0


@dataclass
class RaceResult:
    order: List[str]
    finish_times: dict[str, float]


class Race:
    """Simulate riders along a given route."""

    def __init__(self, riders: List[Rider], route: Route, dt: float = 0.2):
        self.riders = riders
        self.route = route
        self.dt = dt
        self.time = 0.0

    def step(self) -> None:
        """Advance the race by one timestep."""

        # Sort riders by position (front first) for drafting logic.
        self.riders.sort(key=lambda r: r.position, reverse=True)

        for idx, rider in enumerate(self.riders):
            if rider.finished:
                continue

            leader = self.riders[idx - 1] if idx > 0 else None
            gap = (leader.position - rider.position) if leader else float("inf")

            draft_factor = compute_draft_factor(gap)
            gradient = self.route.gradient_at(rider.position)

            power = rider.choose_power({
                "time": self.time,
                "gap": gap if gap != float("inf") else 0.0,
                "at_front": leader is None,
                "draft_factor": draft_factor,
                "gradient": gradient,
            })

            acceleration, next_speed = compute_next_speed(
                power=power,
                speed=rider.velocity,
                gradient=gradient,
                mass=rider.mass,
                cda=rider.cda,
                crr=rider.crr,
                draft_factor=draft_factor,
                dt=self.dt,
            )

            # Update physiology and kinematics.
            rider.physiology.update(power, self.dt)
            rider.velocity = next_speed
            rider.position += rider.velocity * self.dt

            # Prevent excessive overlap: maintain small spacing behind leader.
            if leader and rider.position > leader.position - 0.3:
                rider.position = leader.position - 0.3
                rider.velocity = min(rider.velocity, leader.velocity)

            # Finish line check.
            if rider.position >= self.route.total_length:
                rider.finished = True
                rider.finish_time = self.time
                rider.position = self.route.total_length

        self.time += self.dt

    def run(self, max_time: float = 7200.0) -> RaceResult:
        """Run the simulation until a rider finishes or time cap is hit."""

        max_steps = int(max_time / self.dt)
        for _ in range(max_steps):
            if any(r.finished for r in self.riders):
                break
            self.step()

        # If nobody finishes, mark riders by distance (DNF scenario).
        if not any(r.finished for r in self.riders):
            for rider in self.riders:
                rider.finished = True
                rider.finish_time = max_time

        # Sort final order by position then time.
        self.riders.sort(key=lambda r: (-r.position, r.finish_time or float("inf")))
        order = [r.name for r in self.riders]
        finish_times = {r.name: r.finish_time or max_time for r in self.riders}
        return RaceResult(order=order, finish_times=finish_times)
