"""
Cerebrum Motor System - Drawing Control Layer

The Motor system provides a unified interface for controlling drawing applications,
mimicking the motor control of a human artist's hand. It translates high-level
drawing commands into application-specific operations.

Main Components:
    - MotorInterface: Main API for drawing operations
    - Backend adapters: Application-specific implementations (Krita, simulation)
    - Stroke processors: Convert vector data to drawing commands
    - Tool management: Handle brush, pen, eraser configurations
"""

from motor.core.motor_interface import MotorInterface
from motor.core.stroke import Stroke, StrokePoint
from motor.core.tool import Tool, ToolType, BrushConfig, ToolPresets
from motor.core.canvas import Canvas, Layer

__version__ = "0.1.0"
__all__ = [
    "MotorInterface",
    "Stroke",
    "StrokePoint",
    "Tool",
    "ToolType",
    "BrushConfig",
    "ToolPresets",
    "Canvas",
    "Layer",
]
