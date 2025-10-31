"""
Path processing utilities.

Functions for converting and processing drawing paths from various formats.
"""

from typing import List, Tuple, Optional
import math
import re

from motor.core.stroke import Stroke, StrokePoint


def svg_to_stroke(svg_path: str, sample_rate: int = 50) -> Stroke:
    """
    Convert an SVG path string to a Stroke.
    
    Args:
        svg_path: SVG path data (e.g., "M 10,10 L 20,20 C 30,30 40,40 50,50")
        sample_rate: Number of points to sample from curves
        
    Returns:
        Stroke object with sampled points
    """
    points = []
    current_pos = (0.0, 0.0)
    
    # Parse SVG path commands
    # Simplified parser for basic commands (M, L, C, Q)
    commands = re.findall(r'[MLCQZmlcqz][^MLCQZmlcqz]*', svg_path)
    
    for cmd in commands:
        cmd_type = cmd[0]
        coords_str = cmd[1:].strip()
        
        if not coords_str and cmd_type.upper() not in ['Z']:
            continue
        
        # Parse coordinates
        coords = []
        if coords_str:
            coord_parts = re.findall(r'-?\d+\.?\d*', coords_str)
            coords = [float(c) for c in coord_parts]
        
        # Handle command types
        if cmd_type in ['M', 'm']:  # Move
            if cmd_type == 'M':  # Absolute
                current_pos = (coords[0], coords[1])
            else:  # Relative
                current_pos = (current_pos[0] + coords[0], current_pos[1] + coords[1])
            
            points.append(StrokePoint(x=current_pos[0], y=current_pos[1]))
        
        elif cmd_type in ['L', 'l']:  # Line
            for i in range(0, len(coords), 2):
                if cmd_type == 'L':  # Absolute
                    x, y = coords[i], coords[i + 1]
                else:  # Relative
                    x = current_pos[0] + coords[i]
                    y = current_pos[1] + coords[i + 1]
                
                current_pos = (x, y)
                points.append(StrokePoint(x=x, y=y))
        
        elif cmd_type in ['C', 'c']:  # Cubic Bezier
            for i in range(0, len(coords), 6):
                if i + 5 >= len(coords):
                    break  # Not enough coordinates
                    
                if cmd_type == 'C':  # Absolute
                    cp1 = (coords[i], coords[i + 1])
                    cp2 = (coords[i + 2], coords[i + 3])
                    end = (coords[i + 4], coords[i + 5])
                else:  # Relative
                    cp1 = (current_pos[0] + coords[i], current_pos[1] + coords[i + 1])
                    cp2 = (current_pos[0] + coords[i + 2], current_pos[1] + coords[i + 3])
                    end = (current_pos[0] + coords[i + 4], current_pos[1] + coords[i + 5])
                
                # Sample bezier curve
                bezier_points = bezier_to_points(
                    current_pos, cp1, cp2, end, sample_rate
                )
                points.extend(bezier_points)
                current_pos = end
        
        elif cmd_type in ['Q', 'q']:  # Quadratic Bezier
            for i in range(0, len(coords), 4):
                if i + 3 >= len(coords):
                    break  # Not enough coordinates
                    
                if cmd_type == 'Q':  # Absolute
                    cp = (coords[i], coords[i + 1])
                    end = (coords[i + 2], coords[i + 3])
                else:  # Relative
                    cp = (current_pos[0] + coords[i], current_pos[1] + coords[i + 1])
                    end = (current_pos[0] + coords[i + 2], current_pos[1] + coords[i + 3])
                
                # Convert quadratic to cubic and sample
                # Cubic control points: cp1 = start + 2/3(cp - start), cp2 = end + 2/3(cp - end)
                cp1 = (
                    current_pos[0] + 2/3 * (cp[0] - current_pos[0]),
                    current_pos[1] + 2/3 * (cp[1] - current_pos[1])
                )
                cp2 = (
                    end[0] + 2/3 * (cp[0] - end[0]),
                    end[1] + 2/3 * (cp[1] - end[1])
                )
                
                bezier_points = bezier_to_points(
                    current_pos, cp1, cp2, end, sample_rate
                )
                points.extend(bezier_points)
                current_pos = end
        
        elif cmd_type in ['Z', 'z']:  # Close path
            if points:
                first_point = points[0]
                if current_pos != (first_point.x, first_point.y):
                    points.append(StrokePoint(x=first_point.x, y=first_point.y))
                    current_pos = (first_point.x, first_point.y)
    
    return Stroke(points=points)


def bezier_to_points(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    num_points: int = 50
) -> List[StrokePoint]:
    """
    Sample points from a cubic Bezier curve.
    
    Args:
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        num_points: Number of points to sample
        
    Returns:
        List of sampled StrokePoints
    """
    points = []
    
    for i in range(num_points):
        t = i / (num_points - 1) if num_points > 1 else 0
        
        # Cubic Bezier formula
        x = (
            (1 - t)**3 * p0[0] +
            3 * (1 - t)**2 * t * p1[0] +
            3 * (1 - t) * t**2 * p2[0] +
            t**3 * p3[0]
        )
        y = (
            (1 - t)**3 * p0[1] +
            3 * (1 - t)**2 * t * p1[1] +
            3 * (1 - t) * t**2 * p2[1] +
            t**3 * p3[1]
        )
        
        points.append(StrokePoint(x=x, y=y))
    
    return points


def smooth_path(points: List[StrokePoint], smoothing: float = 0.5) -> List[StrokePoint]:
    """
    Smooth a path using moving average.
    
    Args:
        points: Input points
        smoothing: Smoothing factor (0.0 = no smoothing, 1.0 = maximum smoothing)
        
    Returns:
        Smoothed points
    """
    if len(points) < 3 or smoothing <= 0:
        return points
    
    # Calculate window size based on smoothing factor
    window_size = max(3, int(5 * smoothing))
    if window_size % 2 == 0:
        window_size += 1
    
    half_window = window_size // 2
    smoothed = []
    
    for i in range(len(points)):
        # Collect points in window
        start_idx = max(0, i - half_window)
        end_idx = min(len(points), i + half_window + 1)
        window_points = points[start_idx:end_idx]
        
        # Average position
        avg_x = sum(p.x for p in window_points) / len(window_points)
        avg_y = sum(p.y for p in window_points) / len(window_points)
        
        # Keep original pressure and other attributes
        smoothed.append(StrokePoint(
            x=avg_x,
            y=avg_y,
            pressure=points[i].pressure,
            tilt_x=points[i].tilt_x,
            tilt_y=points[i].tilt_y,
            rotation=points[i].rotation,
            timestamp=points[i].timestamp,
            velocity=points[i].velocity,
        ))
    
    return smoothed


def resample_path(
    points: List[StrokePoint],
    target_spacing: float
) -> List[StrokePoint]:
    """
    Resample path to have uniform spacing between points.
    
    Args:
        points: Input points
        target_spacing: Target distance between consecutive points
        
    Returns:
        Resampled points
    """
    if len(points) < 2:
        return points
    
    resampled = [points[0]]
    accumulated_distance = 0.0
    
    for i in range(1, len(points)):
        prev = points[i - 1]
        curr = points[i]
        
        segment_length = math.sqrt(
            (curr.x - prev.x) ** 2 + (curr.y - prev.y) ** 2
        )
        
        accumulated_distance += segment_length
        
        # Add interpolated points if spacing exceeded
        while accumulated_distance >= target_spacing:
            # Calculate how far along the segment
            t = (segment_length - (accumulated_distance - target_spacing)) / segment_length
            
            # Interpolate point
            new_point = StrokePoint(
                x=prev.x + t * (curr.x - prev.x),
                y=prev.y + t * (curr.y - prev.y),
                pressure=prev.pressure + t * (curr.pressure - prev.pressure),
                tilt_x=prev.tilt_x + t * (curr.tilt_x - prev.tilt_x),
                tilt_y=prev.tilt_y + t * (curr.tilt_y - prev.tilt_y),
                rotation=prev.rotation + t * (curr.rotation - prev.rotation),
                timestamp=prev.timestamp + t * (curr.timestamp - prev.timestamp),
                velocity=prev.velocity + t * (curr.velocity - prev.velocity),
            )
            resampled.append(new_point)
            
            # Update for next iteration
            accumulated_distance -= target_spacing
            prev = new_point
    
    return resampled


def calculate_velocities(points: List[StrokePoint]) -> List[StrokePoint]:
    """
    Calculate velocity at each point based on distance and time.
    
    Args:
        points: Input points with timestamps
        
    Returns:
        Points with updated velocity values
    """
    if len(points) < 2:
        return points
    
    result = []
    
    for i in range(len(points)):
        if i == 0:
            # First point - use forward difference
            dx = points[1].x - points[0].x
            dy = points[1].y - points[0].y
            dt = points[1].timestamp - points[0].timestamp
        elif i == len(points) - 1:
            # Last point - use backward difference
            dx = points[i].x - points[i - 1].x
            dy = points[i].y - points[i - 1].y
            dt = points[i].timestamp - points[i - 1].timestamp
        else:
            # Middle points - use central difference
            dx = points[i + 1].x - points[i - 1].x
            dy = points[i + 1].y - points[i - 1].y
            dt = points[i + 1].timestamp - points[i - 1].timestamp
        
        # Calculate velocity
        if dt > 0:
            distance = math.sqrt(dx ** 2 + dy ** 2)
            velocity = distance / dt
        else:
            velocity = 0.0
        
        # Create new point with velocity
        new_point = StrokePoint(
            x=points[i].x,
            y=points[i].y,
            pressure=points[i].pressure,
            tilt_x=points[i].tilt_x,
            tilt_y=points[i].tilt_y,
            rotation=points[i].rotation,
            timestamp=points[i].timestamp,
            velocity=velocity,
        )
        result.append(new_point)
    
    return result
