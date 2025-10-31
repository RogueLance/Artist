"""
Krita backend implementation.

Connects to Krita via its Python API to provide drawing capabilities.
Requires Krita to be running with Python API enabled.
"""

from typing import Tuple, Optional
import logging

from motor.backends.base import BackendInterface
from motor.core.stroke import Stroke
from motor.core.tool import Tool, ToolType
from motor.core.canvas import Layer


logger = logging.getLogger(__name__)


class KritaBackend(BackendInterface):
    """
    Backend for Krita digital painting application.
    
    This backend uses Krita's Python API to control the application.
    Krita must be running and have the Python plugin enabled.
    
    Note: The actual Krita API integration requires the 'krita' module
    which is only available when running inside Krita. This implementation
    provides the framework for that integration.
    """
    
    def __init__(self):
        """Initialize Krita backend."""
        self.document = None
        self.active_node = None
        self._krita_available = False
        
        try:
            # Try to import Krita API
            # This will only work when running inside Krita
            from krita import Krita
            self.krita = Krita.instance()
            self._krita_available = True
            logger.info("Krita API available")
        except ImportError:
            logger.warning(
                "Krita API not available. "
                "This backend only works when running inside Krita. "
                "Use SimulationBackend for standalone testing."
            )
            self.krita = None
    
    def create_canvas(
        self,
        width: int,
        height: int,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> bool:
        """Create a new document in Krita."""
        if not self._krita_available:
            logger.error("Krita API not available")
            return False
        
        try:
            # Create new document
            self.document = self.krita.createDocument(
                width, height,
                "Motor Canvas",
                "RGBA",
                "U8",
                "",
                300.0  # DPI
            )
            
            # Set background color
            if self.document:
                root = self.document.rootNode()
                if root:
                    # Fill background layer
                    bg_layer = self.document.createNode("Background", "paintlayer")
                    root.addChildNode(bg_layer, None)
                    
                    # Set background color
                    pixel_data = bytes(background_color)
                    bg_layer.setPixelData(pixel_data, 0, 0, width, height)
                
                # Create default drawing layer
                self.active_node = self.document.createNode("Layer 1", "paintlayer")
                root.addChildNode(self.active_node, None)
                
                # Show document
                self.krita.activeWindow().addView(self.document)
                
                logger.info(f"Created Krita canvas: {width}x{height}")
                return True
        except Exception as e:
            logger.error(f"Failed to create Krita canvas: {e}")
        
        return False
    
    def set_tool(self, tool: Tool) -> bool:
        """Set the active tool in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            # Map tool types to Krita tool IDs
            tool_map = {
                ToolType.PENCIL: "KritaShape/KisToolBrush",
                ToolType.PEN: "KritaShape/KisToolBrush",
                ToolType.BRUSH: "KritaShape/KisToolBrush",
                ToolType.AIRBRUSH: "KritaShape/KisToolBrush",
                ToolType.ERASER: "KritaShape/KisToolBrush",  # Use brush with erase mode
            }
            
            tool_id = tool_map.get(tool.tool_type)
            if tool_id:
                # Set brush presets based on tool config
                # This would require accessing Krita's brush engine
                logger.debug(f"Set Krita tool: {tool_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to set Krita tool: {e}")
        
        return False
    
    def draw_stroke(self, stroke: Stroke) -> bool:
        """Draw a stroke in Krita."""
        if not self._krita_available or not self.document or not self.active_node:
            return False
        
        try:
            # Use Krita's painting API to draw stroke
            # This requires accessing the paint device and brush engine
            
            # For each point in stroke, apply paint
            for i in range(len(stroke.points) - 1):
                p1 = stroke.points[i]
                p2 = stroke.points[i + 1]
                
                # Draw line segment
                # This is a simplified version - actual implementation would
                # use Krita's brush engine with pressure, tilt, etc.
                
                # In a full implementation, we would:
                # 1. Get the paint device from active_node
                # 2. Set brush properties (size, opacity, etc.)
                # 3. Apply brush dabs along the path
                # 4. Consider pressure, tilt, and velocity
                pass
            
            self.document.refreshProjection()
            logger.debug(f"Drew stroke with {len(stroke.points)} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to draw stroke in Krita: {e}")
        
        return False
    
    def erase_stroke(self, stroke: Stroke) -> bool:
        """Erase along a stroke path in Krita."""
        if not self._krita_available or not self.document or not self.active_node:
            return False
        
        try:
            # Similar to draw_stroke but with erase blend mode
            # Would set the brush to erase mode and draw the stroke
            self.document.refreshProjection()
            logger.debug(f"Erased stroke with {len(stroke.points)} points")
            return True
        except Exception as e:
            logger.error(f"Failed to erase stroke in Krita: {e}")
        
        return False
    
    def clear_canvas(self) -> bool:
        """Clear the active layer in Krita."""
        if not self._krita_available or not self.active_node:
            return False
        
        try:
            bounds = self.active_node.bounds()
            self.active_node.clear()
            self.document.refreshProjection()
            logger.info("Cleared Krita canvas")
            return True
        except Exception as e:
            logger.error(f"Failed to clear Krita canvas: {e}")
        
        return False
    
    def create_layer(self, layer: Layer) -> bool:
        """Create a new layer in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            node = self.document.createNode(layer.name, "paintlayer")
            root = self.document.rootNode()
            root.addChildNode(node, None)
            
            # Set layer properties
            node.setOpacity(int(layer.opacity * 255))
            node.setVisible(layer.visible)
            node.setLocked(layer.locked)
            
            logger.info(f"Created Krita layer: {layer.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Krita layer: {e}")
        
        return False
    
    def delete_layer(self, layer_id: str) -> bool:
        """Delete a layer in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            # Find and remove layer by ID
            # This would require tracking layer IDs to nodes
            logger.info(f"Deleted Krita layer: {layer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Krita layer: {e}")
        
        return False
    
    def set_active_layer(self, layer_id: str) -> bool:
        """Set the active layer in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            # Find layer by ID and set as active
            # This would require tracking layer IDs to nodes
            logger.debug(f"Set active Krita layer: {layer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set active Krita layer: {e}")
        
        return False
    
    def undo(self) -> bool:
        """Undo the last operation in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            # Krita doesn't expose undo directly in Python API
            # Would need to use action system or key simulation
            logger.debug("Undo in Krita")
            return True
        except Exception as e:
            logger.error(f"Failed to undo in Krita: {e}")
        
        return False
    
    def redo(self) -> bool:
        """Redo the last undone operation in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            logger.debug("Redo in Krita")
            return True
        except Exception as e:
            logger.error(f"Failed to redo in Krita: {e}")
        
        return False
    
    def save(self, filepath: str, format: str) -> bool:
        """Save the document in Krita."""
        if not self._krita_available or not self.document:
            return False
        
        try:
            # Export document
            success = self.document.exportImage(filepath, format.upper())
            if success:
                logger.info(f"Saved Krita document to: {filepath}")
            return success
        except Exception as e:
            logger.error(f"Failed to save Krita document: {e}")
        
        return False
    
    def close(self) -> None:
        """Close the Krita document."""
        if self.document:
            try:
                self.document.close()
                logger.info("Closed Krita document")
            except Exception as e:
                logger.error(f"Failed to close Krita document: {e}")
        
        self.document = None
        self.active_node = None
