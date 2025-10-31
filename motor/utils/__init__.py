"""Utility functions for the motor system."""

from motor.utils.path_processing import (
    svg_to_stroke,
    bezier_to_points,
    smooth_path,
    resample_path,
)
from motor.utils.stroke_emulation import (
    emulate_pressure,
    emulate_tilt,
    emulate_speed_variation,
)

__all__ = [
    "svg_to_stroke",
    "bezier_to_points",
    "smooth_path",
    "resample_path",
    "emulate_pressure",
    "emulate_tilt",
    "emulate_speed_variation",
]
