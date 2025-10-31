"""
Simulation backend implementation.

A standalone backend that simulates drawing operations using PIL/Pillow.
This is useful for testing and development without requiring a drawing application.
"""

from typing import Tuple, Optional, Dict
import logging
from pathlib import Path
import math

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from motor.backends.base import BackendInterface
from motor.core.stroke import Stroke
from motor.core.tool import Tool, ToolType
from motor.core.canvas import Layer


logger = logging.getLogger(__name__)


class SimulationBackend(BackendInterface):
    """
    Simulation backend using PIL/Pillow for drawing.
    
    This backend provides a standalone drawing implementation that doesn't
    require an external drawing application. It's useful for:
    - Testing motor system functionality
    - Development without Krita
    - Batch processing
    - Headless operation
    """
    
    def __init__(self):
        """Initialize simulation backend."""
        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL/Pillow is required for SimulationBackend. "
                "Install with: pip install Pillow"
            )
        
        self.canvas_image: Optional[Image.Image] = None
        self.layers: Dict[str, Image.Image] = {}
        self.active_layer_id: Optional[str] = None
        self.current_tool: Optional[Tool] = None
        self.undo_stack = []
        self.redo_stack = []
        self.width = 0
        self.height = 0
        
        logger.info("Simulation backend initialized")
    
    def create_canvas(
        self,
        width: int,
        height: int,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> bool:
        """Create a new canvas."""
        try:
            self.width = width
            self.height = height
            
            # Create main canvas
            self.canvas_image = Image.new('RGBA', (width, height), background_color)
            
            # Create default layer
            default_layer_id = "layer_default"
            self.layers[default_layer_id] = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            self.active_layer_id = default_layer_id
            
            logger.info(f"Created simulation canvas: {width}x{height}")
            return True
        except Exception as e:
            logger.error(f"Failed to create simulation canvas: {e}")
            return False
    
    def set_tool(self, tool: Tool) -> bool:
        """Set the current drawing tool."""
        self.current_tool = tool
        logger.debug(f"Set simulation tool: {tool.name}")
        return True
    
    def draw_stroke(self, stroke: Stroke) -> bool:
        """Draw a stroke on the canvas."""
        if not self.canvas_image or not self.active_layer_id:
            logger.error("No canvas or active layer")
            return False
        
        if not stroke.points:
            logger.warning("Empty stroke")
            return False
        
        try:
            # Save state for undo
            self._save_state()
            
            # Get active layer
            layer = self.layers.get(self.active_layer_id)
            if not layer:
                logger.error(f"Active layer not found: {self.active_layer_id}")
                return False
            
            # Create draw object
            draw = ImageDraw.Draw(layer, 'RGBA')
            
            # Get tool settings
            tool = self.current_tool
            if not tool:
                # Use default tool
                size = 5.0
                color = (0, 0, 0, 255)
                opacity = 1.0
            else:
                size = tool.config.size
                color = tool.color if stroke.color is None else stroke.color
                opacity = tool.config.opacity
            
            # Apply opacity to color
            if len(color) == 3:
                color = color + (255,)
            color = color[:3] + (int(color[3] * opacity),)
            
            # Draw stroke as series of circles (brush dabs)
            for i, point in enumerate(stroke.points):
                # Scale coordinates if normalized
                x = point.x if point.x > 1 else point.x * self.width
                y = point.y if point.y > 1 else point.y * self.height
                
                # Apply pressure to size
                point_size = size
                if tool and tool.config.pressure_size:
                    point_size = size * point.pressure
                
                # Draw circle at point
                radius = point_size / 2
                bbox = [
                    x - radius, y - radius,
                    x + radius, y + radius
                ]
                
                # Adjust opacity based on pressure if enabled
                point_color = color
                if tool and tool.config.pressure_opacity:
                    point_opacity = int(color[3] * point.pressure)
                    point_color = color[:3] + (point_opacity,)
                
                draw.ellipse(bbox, fill=point_color)
                
                # Draw connecting lines between points for smooth stroke
                if i > 0:
                    prev_point = stroke.points[i - 1]
                    prev_x = prev_point.x if prev_point.x > 1 else prev_point.x * self.width
                    prev_y = prev_point.y if prev_point.y > 1 else prev_point.y * self.height
                    
                    # Draw line with width
                    draw.line(
                        [(prev_x, prev_y), (x, y)],
                        fill=point_color,
                        width=int(point_size)
                    )
            
            # Composite layers
            self._composite_layers()
            
            logger.debug(f"Drew stroke with {len(stroke.points)} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to draw stroke: {e}")
            return False
    
    def erase_stroke(self, stroke: Stroke) -> bool:
        """Erase along a stroke path."""
        if not self.canvas_image or not self.active_layer_id:
            logger.error("No canvas or active layer")
            return False
        
        try:
            # Save state for undo
            self._save_state()
            
            # Get active layer
            layer = self.layers.get(self.active_layer_id)
            if not layer:
                return False
            
            # Create a mask for erasing
            mask = Image.new('L', (self.width, self.height), 0)
            mask_draw = ImageDraw.Draw(mask)
            
            # Get eraser size
            size = self.current_tool.config.size if self.current_tool else 20.0
            
            # Draw erase path on mask
            for i, point in enumerate(stroke.points):
                x = point.x if point.x > 1 else point.x * self.width
                y = point.y if point.y > 1 else point.y * self.height
                
                point_size = size * point.pressure if point.pressure else size
                radius = point_size / 2
                
                bbox = [x - radius, y - radius, x + radius, y + radius]
                mask_draw.ellipse(bbox, fill=255)
                
                if i > 0:
                    prev_point = stroke.points[i - 1]
                    prev_x = prev_point.x if prev_point.x > 1 else prev_point.x * self.width
                    prev_y = prev_point.y if prev_point.y > 1 else prev_point.y * self.height
                    mask_draw.line(
                        [(prev_x, prev_y), (x, y)],
                        fill=255,
                        width=int(point_size)
                    )
            
            # Apply erase mask to layer
            # Convert layer to have alpha
            layer_data = layer.split()
            if len(layer_data) == 4:
                r, g, b, a = layer_data
                # Reduce alpha where mask is white
                mask_inverted = Image.eval(mask, lambda x: 255 - x)
                new_alpha = ImageDraw.ImageMath.eval("convert(a * m / 255, 'L')", a=a, m=mask_inverted)
                layer.putalpha(new_alpha)
            
            # Composite layers
            self._composite_layers()
            
            logger.debug(f"Erased stroke with {len(stroke.points)} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to erase stroke: {e}")
            return False
    
    def clear_canvas(self) -> bool:
        """Clear the active layer."""
        if not self.active_layer_id or self.active_layer_id not in self.layers:
            return False
        
        try:
            self._save_state()
            
            # Clear active layer
            self.layers[self.active_layer_id] = Image.new(
                'RGBA', (self.width, self.height), (0, 0, 0, 0)
            )
            
            # Composite layers
            self._composite_layers()
            
            logger.info("Cleared active layer")
            return True
        except Exception as e:
            logger.error(f"Failed to clear canvas: {e}")
            return False
    
    def create_layer(self, layer: Layer) -> bool:
        """Create a new layer."""
        if not self.canvas_image:
            return False
        
        try:
            # Create transparent layer
            new_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            self.layers[layer.layer_id] = new_layer
            
            logger.info(f"Created layer: {layer.name} ({layer.layer_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to create layer: {e}")
            return False
    
    def delete_layer(self, layer_id: str) -> bool:
        """Delete a layer."""
        if layer_id not in self.layers:
            return False
        
        try:
            del self.layers[layer_id]
            
            # Update active layer if deleted
            if self.active_layer_id == layer_id:
                self.active_layer_id = list(self.layers.keys())[0] if self.layers else None
            
            # Composite remaining layers
            self._composite_layers()
            
            logger.info(f"Deleted layer: {layer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete layer: {e}")
            return False
    
    def set_active_layer(self, layer_id: str) -> bool:
        """Set the active layer."""
        if layer_id not in self.layers:
            return False
        
        self.active_layer_id = layer_id
        logger.debug(f"Set active layer: {layer_id}")
        return True
    
    def undo(self) -> bool:
        """Undo the last operation."""
        if not self.undo_stack:
            return False
        
        try:
            # Save current state to redo stack
            current_state = self._capture_state()
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.undo_stack.pop()
            self._restore_state(previous_state)
            
            logger.debug("Undo operation")
            return True
        except Exception as e:
            logger.error(f"Failed to undo: {e}")
            return False
    
    def redo(self) -> bool:
        """Redo the last undone operation."""
        if not self.redo_stack:
            return False
        
        try:
            # Save current state to undo stack
            current_state = self._capture_state()
            self.undo_stack.append(current_state)
            
            # Restore next state
            next_state = self.redo_stack.pop()
            self._restore_state(next_state)
            
            logger.debug("Redo operation")
            return True
        except Exception as e:
            logger.error(f"Failed to redo: {e}")
            return False
    
    def save(self, filepath: str, format: str) -> bool:
        """Save the canvas to a file."""
        if not self.canvas_image:
            logger.error("No canvas to save")
            return False
        
        try:
            # Convert format
            format = format.upper()
            if format == 'JPG':
                format = 'JPEG'
            
            # Save image
            if format == 'JPEG':
                # JPEG doesn't support transparency, convert to RGB
                rgb_image = Image.new('RGB', self.canvas_image.size, (255, 255, 255))
                rgb_image.paste(self.canvas_image, mask=self.canvas_image.split()[3])
                rgb_image.save(filepath, format)
            else:
                self.canvas_image.save(filepath, format)
            
            logger.info(f"Saved canvas to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save canvas: {e}")
            return False
    
    def close(self) -> None:
        """Close the backend and cleanup resources."""
        self.canvas_image = None
        self.layers.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logger.info("Simulation backend closed")
    
    def _composite_layers(self) -> None:
        """Composite all layers into the main canvas."""
        if not self.canvas_image:
            return
        
        # Start with background
        result = self.canvas_image.copy()
        
        # Composite each layer
        for layer_id, layer in self.layers.items():
            result = Image.alpha_composite(result, layer)
        
        self.canvas_image = result
    
    def _save_state(self) -> None:
        """Save current state for undo."""
        state = self._capture_state()
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo on new action
    
    def _capture_state(self) -> dict:
        """Capture current state."""
        return {
            'layers': {lid: img.copy() for lid, img in self.layers.items()},
            'canvas': self.canvas_image.copy() if self.canvas_image else None,
        }
    
    def _restore_state(self, state: dict) -> None:
        """Restore a saved state."""
        self.layers = {lid: img.copy() for lid, img in state['layers'].items()}
        self.canvas_image = state['canvas'].copy() if state['canvas'] else None
