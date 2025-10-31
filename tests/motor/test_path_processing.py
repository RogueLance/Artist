"""Tests for path processing utilities."""

import pytest
import math
from motor.core.stroke import Stroke, StrokePoint
from motor.utils.path_processing import (
    svg_to_stroke,
    bezier_to_points,
    smooth_path,
    resample_path,
    calculate_velocities,
)


class TestPathProcessing:
    """Test path processing utilities."""
    
    def test_svg_simple_line(self):
        """Test parsing simple SVG line."""
        svg = "M 10,10 L 20,20"
        stroke = svg_to_stroke(svg)
        
        assert len(stroke.points) >= 2
        assert stroke.points[0].x == 10
        assert stroke.points[0].y == 10
    
    def test_svg_curve(self):
        """Test parsing SVG curve."""
        svg = "M 0,0 C 10,10 20,10 30,0"
        stroke = svg_to_stroke(svg, sample_rate=10)
        
        assert len(stroke.points) >= 10
    
    def test_bezier_to_points(self):
        """Test Bezier curve sampling."""
        points = bezier_to_points(
            (0, 0), (10, 10), (20, 10), (30, 0),
            num_points=10
        )
        
        assert len(points) == 10
        assert points[0].x == 0
        assert points[-1].x == 30
    
    def test_smooth_path(self):
        """Test path smoothing."""
        # Create zigzag path
        points = [
            StrokePoint(x=i, y=10 if i % 2 == 0 else 20)
            for i in range(10)
        ]
        
        smoothed = smooth_path(points, smoothing=0.5)
        
        assert len(smoothed) == len(points)
        # Middle points should be between extremes
        for p in smoothed[1:-1]:
            assert 10 <= p.y <= 20
    
    def test_resample_path(self):
        """Test path resampling."""
        points = [
            StrokePoint(x=0, y=0),
            StrokePoint(x=100, y=0),
        ]
        
        resampled = resample_path(points, target_spacing=10)
        
        # Should have approximately 10 points for 100 pixel distance
        assert len(resampled) >= 8
    
    def test_calculate_velocities(self):
        """Test velocity calculation."""
        points = [
            StrokePoint(x=0, y=0, timestamp=0.0),
            StrokePoint(x=10, y=0, timestamp=1.0),
            StrokePoint(x=20, y=0, timestamp=2.0),
        ]
        
        with_velocities = calculate_velocities(points)
        
        assert len(with_velocities) == 3
        # Velocity should be approximately 10 pixels/second
        assert abs(with_velocities[1].velocity - 10.0) < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
