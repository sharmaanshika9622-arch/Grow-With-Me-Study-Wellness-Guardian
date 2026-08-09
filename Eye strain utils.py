"""
eye_strain_utils.py
--------------------
Detects blinks using the Eye Aspect Ratio (EAR) method with
MediaPipe Face Mesh landmarks, then tracks blink RATE over time
(blinks per minute) as a proxy for eye strain.

Why this matters: normal blink rate is ~15-20/min. When people
stare at a screen, blink rate often drops to 5-7/min, which dries
and strains the eyes. A dropping blink rate is a genuinely useful
early-warning signal.
"""

import math
import time
from collections import deque

# MediaPipe Face Mesh landmark indices for the eyes
# (these are standard indices from the 468-point face mesh)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]


def _euclidean(p1, p2):
    return math.dist(p1, p2)


def eye_aspect_ratio(eye_points):
    """
    eye_points: list of 6 (x, y) landmark coordinates in this order:
    [outer_corner, top1, top2, inner_corner, bottom1, bottom2]

    EAR formula (standard from Soukupová & Čech, 2016):
    EAR = (|top1-bottom2| + |top2-bottom1|) / (2 * |outer-inner|)

    A closed eye has a much smaller EAR than an open eye, so a sharp
    dip in EAR = a blink.
    """
    p1, p2, p3, p4, p5, p6 = eye_points
    vertical_1 = _euclidean(p2, p6)
    vertical_2 = _euclidean(p3, p5)
    horizontal = _euclidean(p1, p4)
    if horizontal == 0:
        return 0
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear


class BlinkTracker:
    """
    Tracks blinks over a rolling time window and reports blinks-per-minute.

    Usage:
        tracker = BlinkTracker()
        ... every frame ...
        tracker.update(current_ear_value)
        rate = tracker.blinks_per_minute()
    """

    def __init__(self, ear_threshold=0.21, window_seconds=60):
        self.ear_threshold = ear_threshold
        self.window_seconds = window_seconds
        self.blink_timestamps = deque()
        self._eye_was_closed = False

    def update(self, ear_value):
        """Call this once per frame with the current average EAR."""
        now = time.time()
        is_closed = ear_value < self.ear_threshold

        # Detect the transition from closed -> open as one completed blink
        if self._eye_was_closed and not is_closed:
            self.blink_timestamps.append(now)

        self._eye_was_closed = is_closed

        # Drop timestamps older than our rolling window
        cutoff = now - self.window_seconds
        while self.blink_timestamps and self.blink_timestamps[0] < cutoff:
            self.blink_timestamps.popleft()

    def blinks_per_minute(self):
        """Extrapolate current window's blink count to a per-minute rate."""
        count = len(self.blink_timestamps)
        if self.window_seconds == 0:
            return 0
        return count * (60.0 / self.window_seconds)
