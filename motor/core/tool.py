"""
Tool configuration and management.

Defines brushes, pens, erasers and their properties.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class ToolType(Enum):
    """Types of drawing tools."""
    PENCIL = "pencil"
    PEN = "pen"
    BRUSH = "brush"
    AIRBRUSH = "airbrush"
    ERASER = "eraser"
    SMUDGE = "smudge"
    FILL = "fill"
    EYEDROPPER = "eyedropper"


class BlendMode(Enum):
    """Blending modes for tools."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    ADD = "add"
    SUBTRACT = "subtract"
    ERASE = "erase"


@dataclass
class BrushConfig:
    """
    Configuration for a brush or drawing tool.
    
    Attributes:
        size: Brush size in pixels
        opacity: Brush opacity (0.0-1.0)
        flow: Paint flow rate (0.0-1.0)
        hardness: Edge hardness (0.0-1.0, 0=soft, 1=hard)
        spacing: Spacing between brush dabs (0.0-1.0)
        angle: Brush rotation angle in degrees
        pressure_size: Use pressure to control size
        pressure_opacity: Use pressure to control opacity
        pressure_hardness: Use pressure to control hardness
        tilt_angle: Use tilt to control angle
        blend_mode: Blending mode
        anti_alias: Enable anti-aliasing
        smoothing: Stroke smoothing level (0.0-1.0)
    """
    size: float = 5.0
    opacity: float = 1.0
    flow: float = 1.0
    hardness: float = 0.8
    spacing: float = 0.1
    angle: float = 0.0
    pressure_size: bool = True
    pressure_opacity: bool = False
    pressure_hardness: bool = False
    tilt_angle: bool = False
    blend_mode: BlendMode = BlendMode.NORMAL
    anti_alias: bool = True
    smoothing: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "size": self.size,
            "opacity": self.opacity,
            "flow": self.flow,
            "hardness": self.hardness,
            "spacing": self.spacing,
            "angle": self.angle,
            "pressure_size": self.pressure_size,
            "pressure_opacity": self.pressure_opacity,
            "pressure_hardness": self.pressure_hardness,
            "tilt_angle": self.tilt_angle,
            "blend_mode": self.blend_mode.value,
            "anti_alias": self.anti_alias,
            "smoothing": self.smoothing,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrushConfig':
        """Create from dictionary."""
        data = data.copy()
        if "blend_mode" in data and isinstance(data["blend_mode"], str):
            data["blend_mode"] = BlendMode(data["blend_mode"])
        return cls(**data)


@dataclass
class Tool:
    """
    Represents a drawing tool with its configuration.
    
    This encapsulates both the tool type (pencil, brush, etc.) and its
    specific settings (size, opacity, etc.).
    """
    tool_type: ToolType
    config: BrushConfig = field(default_factory=BrushConfig)
    name: Optional[str] = None
    tool_id: Optional[str] = None
    color: tuple = (0, 0, 0, 255)  # RGBA
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.tool_id is None:
            import uuid
            self.tool_id = f"{self.tool_type.value}_{uuid.uuid4().hex[:8]}"
        if self.name is None:
            self.name = self.tool_type.value.title()
    
    def clone(self) -> 'Tool':
        """Create a copy of this tool."""
        import copy
        return Tool(
            tool_type=self.tool_type,
            config=copy.deepcopy(self.config),
            name=self.name,
            tool_id=None,  # Generate new ID
            color=self.color,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_type": self.tool_type.value,
            "config": self.config.to_dict(),
            "name": self.name,
            "tool_id": self.tool_id,
            "color": self.color,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tool':
        """Create from dictionary."""
        return cls(
            tool_type=ToolType(data["tool_type"]),
            config=BrushConfig.from_dict(data.get("config", {})),
            name=data.get("name"),
            tool_id=data.get("tool_id"),
            color=tuple(data.get("color", (0, 0, 0, 255))),
        )


# Preset tools
class ToolPresets:
    """Common tool presets for quick access."""
    
    @staticmethod
    def pencil(size: float = 2.0) -> Tool:
        """Create a pencil tool."""
        return Tool(
            tool_type=ToolType.PENCIL,
            config=BrushConfig(
                size=size,
                opacity=0.8,
                hardness=1.0,
                spacing=0.05,
                pressure_size=True,
                smoothing=0.2,
            ),
            name="Pencil"
        )
    
    @staticmethod
    def pen(size: float = 3.0) -> Tool:
        """Create a pen tool."""
        return Tool(
            tool_type=ToolType.PEN,
            config=BrushConfig(
                size=size,
                opacity=1.0,
                hardness=1.0,
                spacing=0.01,
                pressure_size=False,
                smoothing=0.3,
            ),
            name="Pen"
        )
    
    @staticmethod
    def brush(size: float = 20.0) -> Tool:
        """Create a soft brush tool."""
        return Tool(
            tool_type=ToolType.BRUSH,
            config=BrushConfig(
                size=size,
                opacity=0.6,
                flow=0.5,
                hardness=0.3,
                spacing=0.15,
                pressure_size=True,
                pressure_opacity=True,
                smoothing=0.5,
            ),
            name="Soft Brush"
        )
    
    @staticmethod
    def eraser(size: float = 20.0) -> Tool:
        """Create an eraser tool."""
        return Tool(
            tool_type=ToolType.ERASER,
            config=BrushConfig(
                size=size,
                opacity=1.0,
                hardness=0.8,
                spacing=0.1,
                pressure_size=True,
                blend_mode=BlendMode.ERASE,
            ),
            name="Eraser"
        )
    
    @staticmethod
    def airbrush(size: float = 30.0) -> Tool:
        """Create an airbrush tool."""
        return Tool(
            tool_type=ToolType.AIRBRUSH,
            config=BrushConfig(
                size=size,
                opacity=0.3,
                flow=0.2,
                hardness=0.0,
                spacing=0.2,
                pressure_opacity=True,
                smoothing=0.6,
            ),
            name="Airbrush"
        )
