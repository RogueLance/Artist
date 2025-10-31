"""
Canvas and layer management.

Manages the drawing surface, layers, and their properties.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
import uuid


class BlendMode(Enum):
    """Layer blending modes."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    ADD = "add"
    SUBTRACT = "subtract"


@dataclass
class Layer:
    """
    Represents a drawing layer.
    
    Layers allow organizing drawing into separate compositable surfaces,
    similar to transparent sheets stacked on top of each other.
    """
    name: str
    layer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "layer_id": self.layer_id,
            "visible": self.visible,
            "locked": self.locked,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode.value,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Layer':
        """Create from dictionary."""
        data = data.copy()
        if "blend_mode" in data and isinstance(data["blend_mode"], str):
            data["blend_mode"] = BlendMode(data["blend_mode"])
        return cls(**data)


@dataclass
class Canvas:
    """
    Represents the drawing canvas.
    
    The canvas is the main drawing surface that contains layers and
    defines the working area dimensions.
    """
    width: int
    height: int
    canvas_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled"
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)  # RGBA
    dpi: int = 300
    layers: List[Layer] = field(default_factory=list)
    active_layer_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize with default layer if empty."""
        if not self.layers:
            default_layer = Layer(name="Layer 1")
            self.layers.append(default_layer)
            self.active_layer_id = default_layer.layer_id
    
    def add_layer(self, name: str, position: Optional[int] = None) -> Layer:
        """
        Add a new layer to the canvas.
        
        Args:
            name: Name for the new layer
            position: Insert position (None = top)
            
        Returns:
            The created layer
        """
        layer = Layer(name=name)
        if position is None:
            self.layers.append(layer)
        else:
            self.layers.insert(position, len(self.layers) - position)
        return layer
    
    def remove_layer(self, layer_id: str) -> bool:
        """
        Remove a layer by ID.
        
        Args:
            layer_id: ID of layer to remove
            
        Returns:
            True if layer was removed
        """
        for i, layer in enumerate(self.layers):
            if layer.layer_id == layer_id:
                self.layers.pop(i)
                # Update active layer if removed
                if self.active_layer_id == layer_id:
                    self.active_layer_id = self.layers[0].layer_id if self.layers else None
                return True
        return False
    
    def get_layer(self, layer_id: str) -> Optional[Layer]:
        """Get layer by ID."""
        for layer in self.layers:
            if layer.layer_id == layer_id:
                return layer
        return None
    
    def get_active_layer(self) -> Optional[Layer]:
        """Get the currently active layer."""
        if self.active_layer_id:
            return self.get_layer(self.active_layer_id)
        return self.layers[0] if self.layers else None
    
    def set_active_layer(self, layer_id: str) -> bool:
        """
        Set the active layer.
        
        Args:
            layer_id: ID of layer to activate
            
        Returns:
            True if layer was found and activated
        """
        if self.get_layer(layer_id):
            self.active_layer_id = layer_id
            return True
        return False
    
    def move_layer(self, layer_id: str, new_position: int) -> bool:
        """
        Move a layer to a new position.
        
        Args:
            layer_id: ID of layer to move
            new_position: New position (0 = bottom)
            
        Returns:
            True if layer was moved
        """
        for i, layer in enumerate(self.layers):
            if layer.layer_id == layer_id:
                self.layers.pop(i)
                # Adjust position if it's beyond current length
                new_position = min(new_position, len(self.layers))
                self.layers.insert(new_position, layer)
                return True
        return False
    
    def get_layer_index(self, layer_id: str) -> int:
        """Get the index of a layer (-1 if not found)."""
        for i, layer in enumerate(self.layers):
            if layer.layer_id == layer_id:
                return i
        return -1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "canvas_id": self.canvas_id,
            "name": self.name,
            "background_color": self.background_color,
            "dpi": self.dpi,
            "layers": [layer.to_dict() for layer in self.layers],
            "active_layer_id": self.active_layer_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Canvas':
        """Create from dictionary."""
        data = data.copy()
        data["layers"] = [Layer.from_dict(l) for l in data.get("layers", [])]
        data["background_color"] = tuple(data.get("background_color", (255, 255, 255, 255)))
        return cls(**data)
