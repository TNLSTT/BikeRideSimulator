"""Example script to run a batch of race simulations."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass

from .simulator import SimulationConfig, Simulator, default_route


@dataclass
class RiderSnapshot:
    name: str
    mass: float
    cp: float
    w_prime: float
    cda: float
    crr: float
    sprint: float


def _sample_riders_for_display(seed: int, count: int) -> list[RiderSnapshot]:
    """Generate rider stats using the same distributions as Simulator.random_rider."""

    rng = random.Random(seed)
    riders: list[RiderSnapshot] = []
    for idx in range(count):
        riders.append(
            RiderSnapshot(
                name=f"Rider_{idx}",
                mass=rng.uniform(65, 80),
                cp=rng.uniform(280, 360),
                w_prime=rng.uniform(15000, 25000),
                cda=rng.uniform(0.25, 0.35),
                crr=rng.uniform(0.003, 0.005),
                sprint=rng.uniform(900, 1300),
            )
        )
    return riders


def main() -> None:
    # Keeping a fixed seed makes repeated runs deterministic. Change or remove this
    # value to explore different random draws.
    seed = 42
    random.seed(seed)

    route = default_route()
    config = SimulationConfig(races=100, dt=0.2)
    simulator = Simulator(route, config)

    # Preview the traits for the first race (same seed used for the actual run).
    sample_riders = _sample_riders_for_display(seed, count=5)
    print("First-race rider traits (using seed 42):")
    for rider in sample_riders:
        print(
            f"  {rider.name}: mass={rider.mass:.2f} kg, "
            f"cp={rider.cp:.0f} W, w'={rider.w_prime:.0f} J, "
            f"cda={rider.cda:.3f}, crr={rider.crr:.4f}, sprint={rider.sprint:.0f} W"
        )

    print("\nRoute profile:")
    print(f"  Total length: {route.total_length/1000:.2f} km")
    for i, segment in enumerate(route.segments, 1):
        pct = segment.gradient * 100
        print(f"  Segment {i}: {segment.length/1000:.2f} km at {pct:+.1f}%")

    print("\nSimulation config:")
    print(f"  Races: {config.races}, dt: {config.dt}s, drafting: {config.draft}")

    summary = simulator.run()

    wins = Counter(summary["wins"]).most_common()
    print("\nWinner histogram (fraction of races):")
    for name, fraction in wins:
        print(f"  {name}: {fraction:.2f}")

    print("\nSample winner traits (averages):")
    for trait, values in summary["traits"].items():
        avg = sum(values) / len(values)
        print(f"  {trait}: {avg:.2f}")


if __name__ == "__main__":
    main()
