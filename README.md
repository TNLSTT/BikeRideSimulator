# BikeRideSimulator

BikeRideSimulator is a lightweight Monte Carlo simulator for evaluating how different rider physiologies perform on a mixed-terrain course.

## Requirements
- Python 3.10+
- No third-party dependencies required.

## How to run the example simulation
1. From the repository root, run the bundled example script:
   ```bash
   python -m cycling_sim.run_example
   ```
2. After a short simulation, the script prints a histogram of winners across 100 races along with average traits of the winning riders.

## Project structure
- `cycling_sim/` contains the simulation logic, including riders, physiology, routes, and the race engine.
- `cycling_sim/run_example.py` provides the ready-to-run example script described above.

## Notes
Feel free to adjust parameters in `cycling_sim/run_example.py` (such as the number of races or route definition) to explore different scenarios.
