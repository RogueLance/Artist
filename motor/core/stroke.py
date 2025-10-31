"""
Stroke representation and manipulation.

A stroke represents a continuous drawing action with multiple points,
each having position, pressure, tilt, and timing information.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import time


class StrokeType(Enum):
    """Type of stroke operation."""
    DRAW = "draw"
    ERASE = "erase"


@dataclass
class StrokePoint:
    """
    A single point in a stroke.
    
    Attributes:
        x: X coordinate (0-1 normalized or absolute pixels)
        y: Y coordinate (0-1 normalized or absolute pixels)
        pressure: Pen pressure (0.0-1.0)
        tilt_x: Pen tilt in X direction (-1.0 to 1.0)
        tilt_y: Pen tilt in Y direction (-1.0 to 1.0)
        rotation: Pen rotation in degrees (0-360)
        timestamp: Time offset from stroke start in seconds
        velocity: Stroke velocity at this point (pixels per second)
    """
    x: float
    y: float
    pressure: float = 1.0
    tilt_x: float = 0.0
    tilt_y: float = 0.0
    rotation: float = 0.0
    timestamp: float = 0.0
    velocity: float = 0.0
    
    def to_tuple(self) -> Tuple[float, float]:
        """Return (x, y) coordinates as tuple."""
        return (self.x, self.y)
    
    def distance_to(self, other: 'StrokePoint') -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Stroke:
    """
    Represents a complete stroke with multiple points.
    
    This is the fundamental unit of drawing that the motor system executes.
    It encapsulates all the information needed to reproduce a drawing action.
    """
    points: List[StrokePoint] = field(default_factory=list)
    stroke_type: StrokeType = StrokeType.DRAW
    tool_id: Optional[str] = None
    layer_id: Optional[str] = None
    color: Optional[Tuple[int, int, int, int]] = None  # RGBA
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and process stroke data."""
        if not self.points:
            self.points = []
    
    def add_point(self, point: StrokePoint) -> None:
        """Add a point to the stroke."""
        self.points.append(point)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get bounding box of the stroke.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.points:
            return (0, 0, 0, 0)
        
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
    
    def length(self) -> float:
        """Calculate total length of the stroke."""
        if len(self.points) < 2:
            return 0.0
        
        total = 0.0
        for i in range(1, len(self.points)):
            total += self.points[i].distance_to(self.points[i-1])
        return total
    
    def duration(self) -> float:
        """Get total duration of the stroke in seconds."""
        if not self.points:
            return 0.0
        return self.points[-1].timestamp if self.points else 0.0
    
    def resample(self, target_points: int) -> 'Stroke':
        """
        Resample stroke to have a specific number of points.
        
        Args:
            target_points: Desired number of points
            
        Returns:
            New stroke with resampled points
        """
        if len(self.points) < 2 or target_points < 2:
            return self
        
        # Calculate cumulative distances
        distances = [0.0]
        for i in range(1, len(self.points)):
            distances.append(
                distances[-1] + self.points[i].distance_to(self.points[i-1])
            )
        
        total_length = distances[-1]
        if total_length == 0:
            return self
        
        # Resample at uniform intervals
        new_points = []
        target_distance = total_length / (target_points - 1)
        
        for i in range(target_points):
            target_dist = i * target_distance
            
            # Find segment containing this distance
            for j in range(len(distances) - 1):
                if distances[j] <= target_dist <= distances[j + 1]:
                    # Interpolate between points j and j+1
                    segment_length = distances[j + 1] - distances[j]
                    if segment_length == 0:
                        t = 0
                    else:
                        t = (target_dist - distances[j]) / segment_length
                    
                    p1, p2 = self.points[j], self.points[j + 1]
                    new_point = StrokePoint(
                        x=p1.x + t * (p2.x - p1.x),
                        y=p1.y + t * (p2.y - p1.y),
                        pressure=p1.pressure + t * (p2.pressure - p1.pressure),
                        tilt_x=p1.tilt_x + t * (p2.tilt_x - p1.tilt_x),
                        tilt_y=p1.tilt_y + t * (p2.tilt_y - p1.tilt_y),
                        rotation=p1.rotation + t * (p2.rotation - p1.rotation),
                        timestamp=p1.timestamp + t * (p2.timestamp - p1.timestamp),
                        velocity=p1.velocity + t * (p2.velocity - p1.velocity),
                    )
                    new_points.append(new_point)
                    break
        
        return Stroke(
            points=new_points,
            stroke_type=self.stroke_type,
            tool_id=self.tool_id,
            layer_id=self.layer_id,
            color=self.color,
            metadata=self.metadata.copy()
        )
    
    def to_dict(self) -> dict:
        """Convert stroke to dictionary for serialization."""
        return {
            "points": [
                {
                    "x": p.x, "y": p.y,
                    "pressure": p.pressure,
                    "tilt_x": p.tilt_x, "tilt_y": p.tilt_y,
                    "rotation": p.rotation,
                    "timestamp": p.timestamp,
                    "velocity": p.velocity,
                }
                for p in self.points
            ],
            "stroke_type": self.stroke_type.value,
            "tool_id": self.tool_id,
            "layer_id": self.layer_id,
            "color": self.color,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Stroke':
        """Create stroke from dictionary."""
        points = [
            StrokePoint(**p) for p in data.get("points", [])
        ]
        return cls(
            points=points,
            stroke_type=StrokeType(data.get("stroke_type", "draw")),
            tool_id=data.get("tool_id"),
            layer_id=data.get("layer_id"),
            color=tuple(data["color"]) if data.get("color") else None,
            metadata=data.get("metadata", {}),
        )
