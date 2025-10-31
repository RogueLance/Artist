"""
Geometry utility functions.

Mathematical operations for 2D/3D geometry and spatial analysis.
"""

from typing import Tuple, List, Optional
import numpy as np


class GeometryUtils:
    """
    Utility functions for geometric calculations.
    """
    
    @staticmethod
    def calculate_distance(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        Calculate Euclidean distance between two 2D points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            Distance
        """
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return float(np.sqrt(dx * dx + dy * dy))
    
    @staticmethod
    def calculate_angle(
        point1: Tuple[float, float],
        vertex: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        Calculate angle at vertex between two points.
        
        Args:
            point1: First point
            vertex: Vertex point
            point2: Second point
            
        Returns:
            Angle in degrees
        """
        # Create vectors
        v1 = np.array([point1[0] - vertex[0], point1[1] - vertex[1]])
        v2 = np.array([point2[0] - vertex[0], point2[1] - vertex[1]])
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    @staticmethod
    def calculate_midpoint(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        Calculate midpoint between two points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            Midpoint (x, y)
        """
        return (
            (point1[0] + point2[0]) / 2,
            (point1[1] + point2[1]) / 2
        )
    
    @staticmethod
    def calculate_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Calculate centroid of multiple points.
        
        Args:
            points: List of points [(x, y), ...]
            
        Returns:
            Centroid (x, y)
        """
        if not points:
            return (0.0, 0.0)
        
        x_sum = sum(p[0] for p in points)
        y_sum = sum(p[1] for p in points)
        n = len(points)
        
        return (x_sum / n, y_sum / n)
    
    @staticmethod
    def point_to_line_distance(
        point: Tuple[float, float],
        line_start: Tuple[float, float],
        line_end: Tuple[float, float]
    ) -> float:
        """
        Calculate perpendicular distance from point to line.
        
        Args:
            point: Point (x, y)
            line_start: Line start point (x, y)
            line_end: Line end point (x, y)
            
        Returns:
            Distance
        """
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate distance using cross product formula
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        
        if denominator < 1e-6:
            # Line is a point
            return GeometryUtils.calculate_distance(point, line_start)
        
        return numerator / denominator
    
    @staticmethod
    def calculate_bounding_box(
        points: List[Tuple[float, float]]
    ) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate bounding box of points.
        
        Args:
            points: List of points [(x, y), ...]
            
        Returns:
            (min_x, min_y, max_x, max_y) or None if no points
        """
        if not points:
            return None
        
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        return (
            min(x_coords),
            min(y_coords),
            max(x_coords),
            max(y_coords)
        )
    
    @staticmethod
    def normalize_points(
        points: List[Tuple[float, float]],
        target_range: Tuple[float, float] = (0.0, 1.0)
    ) -> List[Tuple[float, float]]:
        """
        Normalize points to target range.
        
        Args:
            points: List of points [(x, y), ...]
            target_range: Target range (min, max)
            
        Returns:
            Normalized points
        """
        if not points:
            return []
        
        bounds = GeometryUtils.calculate_bounding_box(points)
        if not bounds:
            return points
        
        min_x, min_y, max_x, max_y = bounds
        range_x = max_x - min_x
        range_y = max_y - min_y
        
        if range_x < 1e-6 or range_y < 1e-6:
            return points
        
        target_min, target_max = target_range
        target_range_val = target_max - target_min
        
        normalized = []
        for x, y in points:
            norm_x = ((x - min_x) / range_x) * target_range_val + target_min
            norm_y = ((y - min_y) / range_y) * target_range_val + target_min
            normalized.append((norm_x, norm_y))
        
        return normalized
    
    @staticmethod
    def calculate_polygon_area(points: List[Tuple[float, float]]) -> float:
        """
        Calculate area of polygon defined by points.
        
        Args:
            points: List of points in order [(x, y), ...]
            
        Returns:
            Area
        """
        if len(points) < 3:
            return 0.0
        
        # Shoelace formula
        area = 0.0
        n = len(points)
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2.0
    
    @staticmethod
    def rotate_point(
        point: Tuple[float, float],
        center: Tuple[float, float],
        angle_degrees: float
    ) -> Tuple[float, float]:
        """
        Rotate point around center.
        
        Args:
            point: Point to rotate (x, y)
            center: Center of rotation (x, y)
            angle_degrees: Rotation angle in degrees
            
        Returns:
            Rotated point (x, y)
        """
        angle_rad = np.radians(angle_degrees)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Translate to origin
        x = point[0] - center[0]
        y = point[1] - center[1]
        
        # Rotate
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a
        
        # Translate back
        return (x_rot + center[0], y_rot + center[1])
