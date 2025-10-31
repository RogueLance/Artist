"""Core motor system components."""

from motor.core.motor_interface import MotorInterface
from motor.core.stroke import Stroke, StrokePoint
from motor.core.tool import Tool, ToolType, BrushConfig
from motor.core.canvas import Canvas, Layer

__all__ = [
    "MotorInterface",
    "Stroke",
    "StrokePoint",
    "Tool",
    "ToolType",
    "BrushConfig",
    "Canvas",
    "Layer",
]
