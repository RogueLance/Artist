"""Tests for stroke emulation utilities."""

import pytest
from motor.core.stroke import Stroke, StrokePoint
from motor.utils.stroke_emulation import (
    emulate_pressure,
    emulate_tilt,
    emulate_speed_variation,
    add_tremor,
    humanize_stroke,
)


class TestStrokeEmulation:
    """Test stroke emulation utilities."""
    
    def test_emulate_pressure(self):
        """Test pressure emulation."""
        points = [StrokePoint(x=i * 10, y=100) for i in range(10)]
        stroke = Stroke(points=points)
        
        emulated = emulate_pressure(
            stroke,
            base_pressure=0.7,
            variation=0.1,
            fade_in=True,
            fade_out=True
        )
        
        assert len(emulated.points) == len(stroke.points)
        # First point should have lower pressure (fade in)
        assert emulated.points[0].pressure < emulated.points[5].pressure
        # Last point should have lower pressure (fade out)
        assert emulated.points[-1].pressure < emulated.points[5].pressure
    
    def test_emulate_tilt(self):
        """Test tilt emulation."""
        points = [StrokePoint(x=i * 10, y=100) for i in range(10)]
        stroke = Stroke(points=points)
        
        tilted = emulate_tilt(
            stroke,
            tilt_angle=45.0,
            tilt_direction=0.0
        )
        
        assert len(tilted.points) == len(stroke.points)
        # Should have non-zero tilt values
        assert any(p.tilt_x != 0 or p.tilt_y != 0 for p in tilted.points)
    
    def test_emulate_speed_variation(self):
        """Test speed variation."""
        points = [StrokePoint(x=i * 10, y=100) for i in range(10)]
        stroke = Stroke(points=points)
        
        varied = emulate_speed_variation(
            stroke,
            duration=2.0,
            speed_curve="ease"
        )
        
        assert len(varied.points) == len(stroke.points)
        # Last point should have timestamp near duration
        assert abs(varied.points[-1].timestamp - 2.0) < 0.1
    
    def test_add_tremor(self):
        """Test tremor addition."""
        points = [StrokePoint(x=100, y=100) for _ in range(10)]
        stroke = Stroke(points=points)
        
        tremored = add_tremor(stroke, amplitude=2.0, frequency=5.0)
        
        assert len(tremored.points) == len(stroke.points)
        # Points should be displaced from original
        assert any(p.x != 100 or p.y != 100 for p in tremored.points)
    
    def test_humanize_stroke(self):
        """Test combined humanization."""
        points = [StrokePoint(x=i * 10, y=100) for i in range(20)]
        stroke = Stroke(points=points)
        
        humanized = humanize_stroke(
            stroke,
            pressure_variation=0.2,
            tilt_angle=30.0,
            tremor_amount=0.5,
            duration=1.5
        )
        
        assert len(humanized.points) == len(stroke.points)
        # Should have varied pressure
        pressures = [p.pressure for p in humanized.points]
        assert min(pressures) != max(pressures)
        # Should have tilt
        assert any(p.tilt_x != 0 for p in humanized.points)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
