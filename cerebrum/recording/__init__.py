"""
Recording module for session capture and time-lapse generation.
"""

from cerebrum.recording.session_recorder import SessionRecorder, CanvasSnapshot
from cerebrum.recording.timelapse import TimelapseGenerator

__all__ = [
    "SessionRecorder",
    "CanvasSnapshot",
    "TimelapseGenerator",
]
