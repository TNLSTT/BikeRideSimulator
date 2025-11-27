"""Route representation for the 1-D race."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class RouteSegment:
    length: float  # meters
    gradient: float  # decimal (0.05 == 5%)


class Route:
    """A route is a sequence of segments with constant gradient."""

    def __init__(self, segments: List[RouteSegment]):
        self.segments = segments
        self.total_length = sum(seg.length for seg in segments)

    def terrain_profile(self) -> list[dict[str, float | str]]:
        """Return a descriptive profile of the route's segments.

        Each entry includes the segment index (1-based), length in kilometers,
        gradient percentage, and a simple terrain label (flat, climb, descent).
        """

        profile: list[dict[str, float | str]] = []

        for idx, seg in enumerate(self.segments, start=1):
            if abs(seg.gradient) < 0.005:
                terrain = "flat"
            elif seg.gradient > 0:
                terrain = "climb"
            else:
                terrain = "descent"

            profile.append(
                {
                    "segment": idx,
                    "length_km": seg.length / 1000.0,
                    "gradient_pct": seg.gradient * 100.0,
                    "terrain": terrain,
                }
            )

        return profile

    def gradient_at(self, position: float) -> float:
        """Return gradient for the given position along the course."""

        pos = 0.0
        for seg in self.segments:
            if position <= pos + seg.length:
                return seg.gradient
            pos += seg.length
        return self.segments[-1].gradient
