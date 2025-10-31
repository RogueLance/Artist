"""
Base interface for drawing backends.

All backend implementations must inherit from BackendInterface and implement
its methods to provide application-specific drawing capabilities.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional

from motor.core.stroke import Stroke
from motor.core.tool import Tool
from motor.core.canvas import Layer


class BackendInterface(ABC):
    """
    Abstract base class for drawing application backends.
    
    This defines the contract that all backends must implement to provide
    drawing capabilities. Backends translate high-level drawing commands
    into application-specific operations.
    """
    
    @abstractmethod
    def create_canvas(
        self,
        width: int,
        height: int,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> bool:
        """
        Create a new canvas in the drawing application.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            background_color: Background color as RGBA tuple
            
        Returns:
            True if canvas was created successfully
        """
        pass
    
    @abstractmethod
    def set_tool(self, tool: Tool) -> bool:
        """
        Set the current drawing tool.
        
        Args:
            tool: Tool to activate
            
        Returns:
            True if tool was set successfully
        """
        pass
    
    @abstractmethod
    def draw_stroke(self, stroke: Stroke) -> bool:
        """
        Draw a stroke on the canvas.
        
        Args:
            stroke: Stroke to draw
            
        Returns:
            True if stroke was drawn successfully
        """
        pass
    
    @abstractmethod
    def erase_stroke(self, stroke: Stroke) -> bool:
        """
        Erase along a stroke path.
        
        Args:
            stroke: Stroke defining erase path
            
        Returns:
            True if erase was successful
        """
        pass
    
    @abstractmethod
    def clear_canvas(self) -> bool:
        """
        Clear the entire canvas.
        
        Returns:
            True if canvas was cleared
        """
        pass
    
    @abstractmethod
    def create_layer(self, layer: Layer) -> bool:
        """
        Create a new layer.
        
        Args:
            layer: Layer to create
            
        Returns:
            True if layer was created
        """
        pass
    
    @abstractmethod
    def delete_layer(self, layer_id: str) -> bool:
        """
        Delete a layer.
        
        Args:
            layer_id: ID of layer to delete
            
        Returns:
            True if layer was deleted
        """
        pass
    
    @abstractmethod
    def set_active_layer(self, layer_id: str) -> bool:
        """
        Set the active drawing layer.
        
        Args:
            layer_id: ID of layer to activate
            
        Returns:
            True if layer was activated
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            True if undo was successful
        """
        pass
    
    @abstractmethod
    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if redo was successful
        """
        pass
    
    @abstractmethod
    def save(self, filepath: str, format: str) -> bool:
        """
        Save the canvas to a file.
        
        Args:
            filepath: Path to save file
            format: Image format
            
        Returns:
            True if save was successful
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the backend and cleanup resources."""
        pass
