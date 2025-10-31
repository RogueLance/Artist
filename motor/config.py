"""
Configuration module for Motor System.

Provides configuration management for motor system settings.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import json


@dataclass
class MotorConfig:
    """
    Configuration for Motor System.
    
    Attributes:
        backend: Default backend to use ("krita" or "simulation")
        default_canvas_width: Default canvas width in pixels
        default_canvas_height: Default canvas height in pixels
        default_dpi: Default DPI resolution
        history_limit: Maximum number of undo steps (None = unlimited)
        auto_save: Enable automatic saving
        auto_save_interval: Auto-save interval in seconds
        output_format: Default output format ("png", "jpg", etc.)
        stroke_smoothing: Default stroke smoothing level (0.0-1.0)
    """
    backend: str = "simulation"
    default_canvas_width: int = 1024
    default_canvas_height: int = 1024
    default_dpi: int = 300
    history_limit: Optional[int] = 100
    auto_save: bool = False
    auto_save_interval: int = 300
    output_format: str = "png"
    stroke_smoothing: float = 0.3
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "backend": self.backend,
            "default_canvas_width": self.default_canvas_width,
            "default_canvas_height": self.default_canvas_height,
            "default_dpi": self.default_dpi,
            "history_limit": self.history_limit,
            "auto_save": self.auto_save,
            "auto_save_interval": self.auto_save_interval,
            "output_format": self.output_format,
            "stroke_smoothing": self.stroke_smoothing,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MotorConfig':
        """Create configuration from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def save(self, filepath: Path) -> None:
        """Save configuration to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path) -> 'MotorConfig':
        """Load configuration from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Default configuration instance
default_config = MotorConfig()
