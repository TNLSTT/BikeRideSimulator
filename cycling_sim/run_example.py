"""Example script to run a batch of race simulations."""

from __future__ import annotations

import random
from collections import Counter

from .simulator import SimulationConfig, Simulator, default_route


def main() -> None:
    random.seed(42)

    route = default_route()
    config = SimulationConfig(races=100, dt=0.2)
    simulator = Simulator(route, config)

    summary = simulator.run()

    wins = Counter(summary["wins"]).most_common()
    print("Winner histogram (fraction of races):")
    for name, fraction in wins:
        print(f"  {name}: {fraction:.2f}")

    print("\nSample winner traits (averages):")
    for trait, values in summary["traits"].items():
        avg = sum(values) / len(values)
        print(f"  {trait}: {avg:.2f}")


if __name__ == "__main__":
    main()
