"""
Main Motor Interface - API for drawing operations.

This is the primary interface that higher-level systems (Vision, Brain) use
to execute drawing commands. It abstracts the underlying drawing application
and provides a unified API.
"""

from typing import Optional, List, Tuple, Union
from pathlib import Path
import logging

from motor.core.stroke import Stroke, StrokePoint, StrokeType
from motor.core.tool import Tool, ToolType, ToolPresets, BrushConfig
from motor.core.canvas import Canvas, Layer
from motor.backends.base import BackendInterface


logger = logging.getLogger(__name__)


class MotorInterface:
    """
    Main interface for controlling drawing operations.
    
    This class provides a high-level API for drawing that is independent of
    the underlying drawing application. It manages tools, canvas state, and
    translates commands to backend-specific operations.
    
    Example:
        >>> motor = MotorInterface(backend="simulation")
        >>> motor.create_canvas(800, 600)
        >>> motor.switch_tool(ToolPresets.pencil(size=5.0))
        >>> stroke = Stroke(points=[...])
        >>> motor.draw_stroke(stroke)
        >>> motor.save("output.png")
    """
    
    def __init__(self, backend: Union[str, BackendInterface] = "simulation"):
        """
        Initialize the motor interface.
        
        Args:
            backend: Backend to use ("krita", "simulation", or BackendInterface instance)
        """
        self.backend = self._init_backend(backend)
        self.canvas: Optional[Canvas] = None
        self.current_tool: Optional[Tool] = None
        self.undo_stack: List[dict] = []
        self.redo_stack: List[dict] = []
        self._history_enabled = True
        
        logger.info(f"Motor interface initialized with backend: {type(self.backend).__name__}")
    
    def _init_backend(self, backend: Union[str, BackendInterface]) -> BackendInterface:
        """Initialize the appropriate backend."""
        if isinstance(backend, BackendInterface):
            return backend
        
        if backend == "krita":
            from motor.backends.krita_backend import KritaBackend
            return KritaBackend()
        elif backend == "simulation":
            from motor.backends.simulation_backend import SimulationBackend
            return SimulationBackend()
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def create_canvas(
        self,
        width: int,
        height: int,
        name: str = "Untitled",
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        dpi: int = 300
    ) -> Canvas:
        """
        Create a new canvas.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            name: Canvas name
            background_color: Background color as RGBA tuple
            dpi: Resolution in dots per inch
            
        Returns:
            The created canvas
        """
        self.canvas = Canvas(
            width=width,
            height=height,
            name=name,
            background_color=background_color,
            dpi=dpi
        )
        
        # Initialize backend canvas
        self.backend.create_canvas(width, height, background_color)
        
        logger.info(f"Created canvas: {width}x{height} @ {dpi}dpi")
        return self.canvas
    
    def get_canvas(self) -> Optional[Canvas]:
        """Get the current canvas."""
        return self.canvas
    
    def switch_tool(self, tool: Tool) -> None:
        """
        Switch to a different drawing tool.
        
        Args:
            tool: Tool to switch to
        """
        self.current_tool = tool
        self.backend.set_tool(tool)
        logger.debug(f"Switched to tool: {tool.name}")
    
    def set_brush(
        self,
        size: Optional[float] = None,
        opacity: Optional[float] = None,
        hardness: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Update brush configuration.
        
        Args:
            size: Brush size in pixels
            opacity: Brush opacity (0.0-1.0)
            hardness: Edge hardness (0.0-1.0)
            **kwargs: Additional brush parameters
        """
        if not self.current_tool:
            self.current_tool = ToolPresets.brush()
        
        if size is not None:
            self.current_tool.config.size = size
        if opacity is not None:
            self.current_tool.config.opacity = opacity
        if hardness is not None:
            self.current_tool.config.hardness = hardness
        
        # Update other parameters
        for key, value in kwargs.items():
            if hasattr(self.current_tool.config, key):
                setattr(self.current_tool.config, key, value)
        
        self.backend.set_tool(self.current_tool)
        logger.debug(f"Updated brush config: size={size}, opacity={opacity}")
    
    def draw_stroke(self, stroke: Stroke) -> bool:
        """
        Draw a stroke on the canvas.
        
        Args:
            stroke: Stroke to draw
            
        Returns:
            True if stroke was drawn successfully
        """
        if not self.canvas:
            logger.error("No canvas available")
            return False
        
        if not stroke.points:
            logger.warning("Empty stroke provided")
            return False
        
        # Set layer if specified
        if stroke.layer_id:
            layer = self.canvas.get_layer(stroke.layer_id)
            if layer:
                self.canvas.set_active_layer(stroke.layer_id)
        
        # Set tool if specified
        if stroke.tool_id and self.current_tool and stroke.tool_id != self.current_tool.tool_id:
            logger.warning(f"Stroke tool_id mismatch (stroke: {stroke.tool_id}, current: {self.current_tool.tool_id})")
        
        # Add to history before drawing
        if self._history_enabled:
            self._add_to_history({
                "action": "draw_stroke",
                "stroke": stroke.to_dict(),
            })
        
        # Execute on backend
        success = self.backend.draw_stroke(stroke)
        
        if success:
            logger.debug(f"Drew stroke with {len(stroke.points)} points")
        else:
            logger.error("Failed to draw stroke")
        
        return success
    
    def erase_stroke(self, stroke: Stroke) -> bool:
        """
        Erase along a stroke path.
        
        Args:
            stroke: Stroke defining erase path
            
        Returns:
            True if erase was successful
        """
        if not self.canvas:
            logger.error("No canvas available")
            return False
        
        # Set stroke type to erase
        stroke.stroke_type = StrokeType.ERASE
        
        # Switch to eraser if not already
        if not self.current_tool or self.current_tool.tool_type != ToolType.ERASER:
            self.switch_tool(ToolPresets.eraser())
        
        # Add to history
        if self._history_enabled:
            self._add_to_history({
                "action": "erase_stroke",
                "stroke": stroke.to_dict(),
            })
        
        # Execute on backend
        success = self.backend.erase_stroke(stroke)
        
        if success:
            logger.debug(f"Erased stroke with {len(stroke.points)} points")
        else:
            logger.error("Failed to erase stroke")
        
        return success
    
    def clear_canvas(self) -> bool:
        """
        Clear the entire canvas.
        
        Returns:
            True if canvas was cleared
        """
        if not self.canvas:
            return False
        
        if self._history_enabled:
            self._add_to_history({"action": "clear_canvas"})
        
        return self.backend.clear_canvas()
    
    def create_layer(self, name: str, position: Optional[int] = None) -> Optional[Layer]:
        """
        Create a new layer.
        
        Args:
            name: Layer name
            position: Insert position (None = top)
            
        Returns:
            The created layer
        """
        if not self.canvas:
            logger.error("No canvas available")
            return None
        
        layer = self.canvas.add_layer(name, position)
        self.backend.create_layer(layer)
        
        logger.info(f"Created layer: {name}")
        return layer
    
    def delete_layer(self, layer_id: str) -> bool:
        """
        Delete a layer.
        
        Args:
            layer_id: ID of layer to delete
            
        Returns:
            True if layer was deleted
        """
        if not self.canvas:
            return False
        
        success = self.canvas.remove_layer(layer_id)
        if success:
            self.backend.delete_layer(layer_id)
            logger.info(f"Deleted layer: {layer_id}")
        
        return success
    
    def set_active_layer(self, layer_id: str) -> bool:
        """
        Set the active drawing layer.
        
        Args:
            layer_id: ID of layer to activate
            
        Returns:
            True if layer was activated
        """
        if not self.canvas:
            return False
        
        success = self.canvas.set_active_layer(layer_id)
        if success:
            self.backend.set_active_layer(layer_id)
            logger.debug(f"Set active layer: {layer_id}")
        
        return success
    
    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            True if undo was successful
        """
        if not self.undo_stack:
            logger.debug("Nothing to undo")
            return False
        
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        
        # Disable history during undo
        self._history_enabled = False
        success = self.backend.undo()
        self._history_enabled = True
        
        logger.debug(f"Undid action: {action.get('action', 'unknown')}")
        return success
    
    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if redo was successful
        """
        if not self.redo_stack:
            logger.debug("Nothing to redo")
            return False
        
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        
        # Disable history during redo
        self._history_enabled = False
        success = self.backend.redo()
        self._history_enabled = True
        
        logger.debug(f"Redid action: {action.get('action', 'unknown')}")
        return success
    
    def save(self, filepath: Union[str, Path], format: Optional[str] = None) -> bool:
        """
        Save the canvas to a file.
        
        Args:
            filepath: Path to save file
            format: Image format (png, jpg, etc.). Auto-detected if None
            
        Returns:
            True if save was successful
        """
        if not self.canvas:
            logger.error("No canvas to save")
            return False
        
        filepath = Path(filepath)
        if format is None:
            format = filepath.suffix[1:] if filepath.suffix else "png"
        
        success = self.backend.save(str(filepath), format)
        
        if success:
            logger.info(f"Saved canvas to: {filepath}")
        else:
            logger.error(f"Failed to save canvas to: {filepath}")
        
        return success
    
    def export(self, filepath: Union[str, Path], **options) -> bool:
        """
        Export the canvas with specific options.
        
        Args:
            filepath: Path to export file
            **options: Export options (format, quality, etc.)
            
        Returns:
            True if export was successful
        """
        return self.save(filepath, options.get("format"))
    
    def get_history(self) -> List[dict]:
        """Get the undo history."""
        return self.undo_stack.copy()
    
    def clear_history(self) -> None:
        """Clear undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        logger.debug("Cleared undo/redo history")
    
    def _add_to_history(self, action: dict) -> None:
        """Add an action to the undo stack."""
        self.undo_stack.append(action)
        self.redo_stack.clear()  # Clear redo stack on new action
    
    def close(self) -> None:
        """Close the motor interface and cleanup resources."""
        self.backend.close()
        logger.info("Motor interface closed")
