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

    def gradient_at(self, position: float) -> float:
        """Return gradient for the given position along the course."""

        pos = 0.0
        for seg in self.segments:
            if position <= pos + seg.length:
                return seg.gradient
            pos += seg.length
        return self.segments[-1].gradient
