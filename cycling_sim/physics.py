"""Physics helpers for cycling dynamics in 1-D.

All equations use SI units. Formulas are simplified but capture the
primary forces affecting a cyclist on the road.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PhysicsConstants:
    """Tunables for environmental and mechanical parameters."""

    air_density: float = 1.226  # kg/m^3 at sea level
    gravity: float = 9.80665  # m/s^2
    drivetrain_efficiency: float = 0.975  # fraction of power reaching the wheel


DEFAULT_CONSTANTS = PhysicsConstants()


def compute_forces(
    speed: float,
    gradient: float,
    mass: float,
    cda: float,
    crr: float,
    draft_factor: float = 1.0,
    constants: PhysicsConstants = DEFAULT_CONSTANTS,
) -> dict[str, float]:
    """Compute resistive forces acting on the rider.

    Args:
        speed: Current ground speed in m/s.
        gradient: Road gradient as a decimal (0.05 == 5%).
        mass: System mass (rider + bike) in kg.
        cda: Effective aerodynamic drag area in m^2.
        crr: Coefficient of rolling resistance (unitless).
        draft_factor: Multiplier applied to CdA when drafting (<1 reduces drag).
        constants: Physical constants.

    Returns:
        Dictionary containing individual forces (Newtons) and total resistance.
    """

    # Aerodynamic drag: F = 0.5 * rho * CdA * v^2
    aero_force = 0.5 * constants.air_density * cda * draft_factor * speed**2

    # Rolling resistance: F = m * g * Crr * cos(theta)
    # For small angles, cos(theta) ~ 1.
    roll_force = mass * constants.gravity * crr

    # Gravitational component along the slope: F = m * g * sin(theta)
    # For small gradients, sin(theta) ~ gradient.
    grade_force = mass * constants.gravity * gradient

    total_resist = aero_force + roll_force + grade_force
    return {
        "aero": aero_force,
        "rolling": roll_force,
        "grade": grade_force,
        "total": total_resist,
    }


def compute_next_speed(
    power: float,
    speed: float,
    gradient: float,
    mass: float,
    cda: float,
    crr: float,
    draft_factor: float = 1.0,
    dt: float = 0.2,
    constants: PhysicsConstants = DEFAULT_CONSTANTS,
) -> tuple[float, float]:
    """Compute acceleration and next speed given rider output.

    Args:
        power: Target power at the pedals (W).
        speed: Current speed (m/s).
        gradient: Road gradient as decimal.
        mass: Rider system mass (kg).
        cda: Aerodynamic drag area (m^2).
        crr: Rolling resistance coefficient.
        draft_factor: Aerodynamic reduction multiplier when drafting.
        dt: Simulation timestep (s).
        constants: Environmental/mechanical constants.

    Returns:
        Tuple of (acceleration m/s^2, new_speed m/s).
    """

    resistive = compute_forces(speed, gradient, mass, cda, crr, draft_factor, constants)

    # Convert power to propulsive force. Avoid division by zero at low speeds by
    # assuming a minimal rolling speed of 0.5 m/s.
    effective_speed = max(speed, 0.5)
    drive_force = (power * constants.drivetrain_efficiency) / effective_speed

    net_force = drive_force - resistive["total"]
    acceleration = net_force / mass

    next_speed = speed + acceleration * dt
    # Clamp to non-negative speeds to avoid numerical issues.
    next_speed = max(0.0, next_speed)

    return acceleration, next_speed
