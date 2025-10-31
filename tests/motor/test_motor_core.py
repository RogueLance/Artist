"""Tests for Motor System core functionality."""

import pytest
from motor.core.stroke import Stroke, StrokePoint, StrokeType
from motor.core.tool import Tool, ToolType, ToolPresets, BrushConfig
from motor.core.canvas import Canvas, Layer
from motor import MotorInterface


class TestStroke:
    """Test Stroke class."""
    
    def test_create_empty_stroke(self):
        """Test creating an empty stroke."""
        stroke = Stroke()
        assert len(stroke.points) == 0
        assert stroke.stroke_type == StrokeType.DRAW
    
    def test_create_stroke_with_points(self):
        """Test creating stroke with points."""
        points = [
            StrokePoint(x=0, y=0),
            StrokePoint(x=10, y=10),
            StrokePoint(x=20, y=20),
        ]
        stroke = Stroke(points=points)
        assert len(stroke.points) == 3
        assert stroke.points[0].x == 0
        assert stroke.points[2].x == 20
    
    def test_stroke_bounds(self):
        """Test getting stroke bounding box."""
        points = [
            StrokePoint(x=10, y=20),
            StrokePoint(x=50, y=40),
            StrokePoint(x=30, y=10),
        ]
        stroke = Stroke(points=points)
        bounds = stroke.get_bounds()
        assert bounds == (10, 10, 50, 40)
    
    def test_stroke_length(self):
        """Test calculating stroke length."""
        points = [
            StrokePoint(x=0, y=0),
            StrokePoint(x=3, y=4),  # Distance = 5
            StrokePoint(x=6, y=8),  # Distance = 5
        ]
        stroke = Stroke(points=points)
        length = stroke.length()
        assert abs(length - 10.0) < 0.01
    
    def test_stroke_serialization(self):
        """Test stroke to/from dict."""
        points = [StrokePoint(x=10, y=20, pressure=0.5)]
        stroke = Stroke(points=points, tool_id="test_tool")
        
        # Serialize
        data = stroke.to_dict()
        assert data["tool_id"] == "test_tool"
        assert len(data["points"]) == 1
        
        # Deserialize
        stroke2 = Stroke.from_dict(data)
        assert stroke2.tool_id == "test_tool"
        assert len(stroke2.points) == 1
        assert stroke2.points[0].x == 10


class TestTool:
    """Test Tool class."""
    
    def test_create_tool(self):
        """Test creating a tool."""
        tool = Tool(tool_type=ToolType.PENCIL)
        assert tool.tool_type == ToolType.PENCIL
        assert tool.tool_id is not None
        assert tool.name == "Pencil"
    
    def test_tool_presets(self):
        """Test tool presets."""
        pencil = ToolPresets.pencil(size=5.0)
        assert pencil.tool_type == ToolType.PENCIL
        assert pencil.config.size == 5.0
        
        brush = ToolPresets.brush(size=20.0)
        assert brush.tool_type == ToolType.BRUSH
        assert brush.config.size == 20.0
    
    def test_tool_clone(self):
        """Test cloning a tool."""
        tool1 = ToolPresets.pen(size=3.0)
        tool2 = tool1.clone()
        
        assert tool2.tool_type == tool1.tool_type
        assert tool2.config.size == tool1.config.size
        assert tool2.tool_id != tool1.tool_id  # Should have new ID
    
    def test_tool_serialization(self):
        """Test tool to/from dict."""
        tool = ToolPresets.brush(size=15.0)
        
        # Serialize
        data = tool.to_dict()
        assert data["tool_type"] == "brush"
        assert data["config"]["size"] == 15.0
        
        # Deserialize
        tool2 = Tool.from_dict(data)
        assert tool2.tool_type == ToolType.BRUSH
        assert tool2.config.size == 15.0


class TestCanvas:
    """Test Canvas class."""
    
    def test_create_canvas(self):
        """Test creating a canvas."""
        canvas = Canvas(width=800, height=600)
        assert canvas.width == 800
        assert canvas.height == 600
        assert len(canvas.layers) == 1  # Default layer
        assert canvas.active_layer_id is not None
    
    def test_add_layer(self):
        """Test adding layers."""
        canvas = Canvas(width=800, height=600)
        initial_count = len(canvas.layers)
        
        layer = canvas.add_layer("New Layer")
        assert len(canvas.layers) == initial_count + 1
        assert layer.name == "New Layer"
    
    def test_remove_layer(self):
        """Test removing layers."""
        canvas = Canvas(width=800, height=600)
        layer = canvas.add_layer("To Remove")
        
        success = canvas.remove_layer(layer.layer_id)
        assert success
        assert canvas.get_layer(layer.layer_id) is None
    
    def test_active_layer(self):
        """Test active layer management."""
        canvas = Canvas(width=800, height=600)
        layer1 = canvas.add_layer("Layer 1")
        layer2 = canvas.add_layer("Layer 2")
        
        canvas.set_active_layer(layer2.layer_id)
        active = canvas.get_active_layer()
        assert active.layer_id == layer2.layer_id
    
    def test_canvas_serialization(self):
        """Test canvas to/from dict."""
        canvas = Canvas(width=800, height=600, name="Test Canvas")
        canvas.add_layer("Extra Layer")
        
        # Serialize
        data = canvas.to_dict()
        assert data["width"] == 800
        assert data["name"] == "Test Canvas"
        assert len(data["layers"]) == 2
        
        # Deserialize
        canvas2 = Canvas.from_dict(data)
        assert canvas2.width == 800
        assert canvas2.name == "Test Canvas"
        assert len(canvas2.layers) == 2


class TestMotorInterface:
    """Test MotorInterface class."""
    
    def test_create_interface(self):
        """Test creating motor interface."""
        motor = MotorInterface(backend="simulation")
        assert motor.backend is not None
        motor.close()
    
    def test_create_canvas(self):
        """Test creating canvas through interface."""
        motor = MotorInterface(backend="simulation")
        canvas = motor.create_canvas(width=800, height=600)
        
        assert canvas is not None
        assert canvas.width == 800
        assert canvas.height == 600
        motor.close()
    
    def test_switch_tool(self):
        """Test switching tools."""
        motor = MotorInterface(backend="simulation")
        motor.create_canvas(800, 600)
        
        pencil = ToolPresets.pencil()
        motor.switch_tool(pencil)
        assert motor.current_tool is not None
        assert motor.current_tool.tool_type == ToolType.PENCIL
        motor.close()
    
    def test_draw_stroke(self):
        """Test drawing a stroke."""
        motor = MotorInterface(backend="simulation")
        motor.create_canvas(800, 600)
        motor.switch_tool(ToolPresets.pencil())
        
        points = [
            StrokePoint(x=100, y=100),
            StrokePoint(x=200, y=200),
        ]
        stroke = Stroke(points=points)
        
        success = motor.draw_stroke(stroke)
        assert success
        motor.close()
    
    def test_undo_redo(self):
        """Test undo/redo functionality."""
        motor = MotorInterface(backend="simulation")
        motor.create_canvas(800, 600)
        motor.switch_tool(ToolPresets.pencil())
        
        # Draw a stroke
        stroke = Stroke(points=[StrokePoint(x=100, y=100)])
        motor.draw_stroke(stroke)
        
        # Undo
        success = motor.undo()
        assert success
        
        # Redo
        success = motor.redo()
        assert success
        
        motor.close()
    
    def test_layer_operations(self):
        """Test layer operations through interface."""
        motor = MotorInterface(backend="simulation")
        motor.create_canvas(800, 600)
        
        # Create layer
        layer = motor.create_layer("Test Layer")
        assert layer is not None
        
        # Set active
        success = motor.set_active_layer(layer.layer_id)
        assert success
        
        # Delete layer
        success = motor.delete_layer(layer.layer_id)
        assert success
        
        motor.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
