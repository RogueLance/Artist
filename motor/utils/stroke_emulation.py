"""
Stroke emulation utilities.

Functions for adding realistic variations to strokes, simulating human-like
drawing behavior with pressure, tilt, and speed variations.
"""

from typing import List
import math
import random

from motor.core.stroke import Stroke, StrokePoint


def emulate_pressure(
    stroke: Stroke,
    base_pressure: float = 0.7,
    variation: float = 0.2,
    fade_in: bool = True,
    fade_out: bool = True
) -> Stroke:
    """
    Add realistic pressure variation to a stroke.
    
    Human artists naturally vary pressure during a stroke, often starting
    light, building up in the middle, and tapering at the end.
    
    Args:
        stroke: Input stroke
        base_pressure: Base pressure level (0.0-1.0)
        variation: Random variation amount (0.0-1.0)
        fade_in: Apply pressure fade-in at start
        fade_out: Apply pressure fade-out at end
        
    Returns:
        New stroke with emulated pressure
    """
    if not stroke.points:
        return stroke
    
    new_points = []
    num_points = len(stroke.points)
    
    for i, point in enumerate(stroke.points):
        t = i / (num_points - 1) if num_points > 1 else 0
        
        # Calculate pressure envelope
        pressure = base_pressure
        
        # Fade in (first 20% of stroke)
        if fade_in and t < 0.2:
            fade_factor = t / 0.2
            pressure *= fade_factor
        
        # Fade out (last 20% of stroke)
        if fade_out and t > 0.8:
            fade_factor = (1.0 - t) / 0.2
            pressure *= fade_factor
        
        # Add random variation
        if variation > 0:
            noise = random.gauss(0, variation)
            pressure += noise
        
        # Clamp to valid range
        pressure = max(0.0, min(1.0, pressure))
        
        new_point = StrokePoint(
            x=point.x,
            y=point.y,
            pressure=pressure,
            tilt_x=point.tilt_x,
            tilt_y=point.tilt_y,
            rotation=point.rotation,
            timestamp=point.timestamp,
            velocity=point.velocity,
        )
        new_points.append(new_point)
    
    return Stroke(
        points=new_points,
        stroke_type=stroke.stroke_type,
        tool_id=stroke.tool_id,
        layer_id=stroke.layer_id,
        color=stroke.color,
        metadata=stroke.metadata.copy()
    )


def emulate_tilt(
    stroke: Stroke,
    tilt_angle: float = 45.0,
    tilt_direction: float = 0.0,
    variation: float = 5.0
) -> Stroke:
    """
    Add pen tilt to a stroke.
    
    Simulates holding a pen at an angle, which affects brush appearance.
    
    Args:
        stroke: Input stroke
        tilt_angle: Tilt angle from vertical in degrees (0-90)
        tilt_direction: Tilt direction in degrees (0-360)
        variation: Random variation in degrees
        
    Returns:
        New stroke with emulated tilt
    """
    if not stroke.points:
        return stroke
    
    new_points = []
    
    for point in stroke.points:
        # Add random variation
        angle = tilt_angle + random.gauss(0, variation)
        direction = tilt_direction + random.gauss(0, variation)
        
        # Clamp angle
        angle = max(0, min(90, angle))
        
        # Convert to tilt_x and tilt_y (-1.0 to 1.0)
        angle_rad = math.radians(angle)
        direction_rad = math.radians(direction)
        
        tilt_x = math.sin(angle_rad) * math.cos(direction_rad)
        tilt_y = math.sin(angle_rad) * math.sin(direction_rad)
        
        new_point = StrokePoint(
            x=point.x,
            y=point.y,
            pressure=point.pressure,
            tilt_x=tilt_x,
            tilt_y=tilt_y,
            rotation=point.rotation,
            timestamp=point.timestamp,
            velocity=point.velocity,
        )
        new_points.append(new_point)
    
    return Stroke(
        points=new_points,
        stroke_type=stroke.stroke_type,
        tool_id=stroke.tool_id,
        layer_id=stroke.layer_id,
        color=stroke.color,
        metadata=stroke.metadata.copy()
    )


def emulate_speed_variation(
    stroke: Stroke,
    duration: float = 1.0,
    speed_curve: str = "ease"
) -> Stroke:
    """
    Add timing variation to simulate drawing speed.
    
    Human artists speed up and slow down during strokes. This adds
    realistic timestamp variation.
    
    Args:
        stroke: Input stroke
        duration: Total stroke duration in seconds
        speed_curve: Speed profile ("linear", "ease", "ease-in", "ease-out")
        
    Returns:
        New stroke with emulated timing
    """
    if not stroke.points or len(stroke.points) < 2:
        return stroke
    
    new_points = []
    num_points = len(stroke.points)
    
    for i, point in enumerate(stroke.points):
        t = i / (num_points - 1) if num_points > 1 else 0
        
        # Apply easing function
        if speed_curve == "linear":
            time_t = t
        elif speed_curve == "ease-in":
            # Slow start, fast end
            time_t = t * t
        elif speed_curve == "ease-out":
            # Fast start, slow end
            time_t = 1 - (1 - t) * (1 - t)
        elif speed_curve == "ease":
            # Ease in and out
            if t < 0.5:
                time_t = 2 * t * t
            else:
                time_t = 1 - 2 * (1 - t) * (1 - t)
        else:
            time_t = t
        
        timestamp = time_t * duration
        
        new_point = StrokePoint(
            x=point.x,
            y=point.y,
            pressure=point.pressure,
            tilt_x=point.tilt_x,
            tilt_y=point.tilt_y,
            rotation=point.rotation,
            timestamp=timestamp,
            velocity=point.velocity,
        )
        new_points.append(new_point)
    
    # Calculate velocities based on new timing
    from motor.utils.path_processing import calculate_velocities
    new_points = calculate_velocities(new_points)
    
    return Stroke(
        points=new_points,
        stroke_type=stroke.stroke_type,
        tool_id=stroke.tool_id,
        layer_id=stroke.layer_id,
        color=stroke.color,
        metadata=stroke.metadata.copy()
    )


def add_tremor(
    stroke: Stroke,
    amplitude: float = 1.0,
    frequency: float = 10.0
) -> Stroke:
    """
    Add hand tremor to a stroke for realism.
    
    Adds small, high-frequency positional noise that simulates natural
    hand shake.
    
    Args:
        stroke: Input stroke
        amplitude: Tremor amplitude in pixels
        frequency: Tremor frequency (oscillations per stroke)
        
    Returns:
        New stroke with tremor
    """
    if not stroke.points:
        return stroke
    
    new_points = []
    num_points = len(stroke.points)
    
    for i, point in enumerate(stroke.points):
        t = i / (num_points - 1) if num_points > 1 else 0
        
        # Add oscillating noise
        phase = t * frequency * 2 * math.pi
        noise_x = amplitude * math.sin(phase + random.random() * 0.5)
        noise_y = amplitude * math.cos(phase + random.random() * 0.5)
        
        new_point = StrokePoint(
            x=point.x + noise_x,
            y=point.y + noise_y,
            pressure=point.pressure,
            tilt_x=point.tilt_x,
            tilt_y=point.tilt_y,
            rotation=point.rotation,
            timestamp=point.timestamp,
            velocity=point.velocity,
        )
        new_points.append(new_point)
    
    return Stroke(
        points=new_points,
        stroke_type=stroke.stroke_type,
        tool_id=stroke.tool_id,
        layer_id=stroke.layer_id,
        color=stroke.color,
        metadata=stroke.metadata.copy()
    )


def humanize_stroke(
    stroke: Stroke,
    pressure_variation: float = 0.2,
    tilt_angle: float = 30.0,
    tremor_amount: float = 0.5,
    duration: float = 1.0
) -> Stroke:
    """
    Apply a combination of humanizing effects to a stroke.
    
    This is a convenience function that applies pressure, tilt, timing,
    and tremor variations in one call.
    
    Args:
        stroke: Input stroke
        pressure_variation: Amount of pressure variation
        tilt_angle: Pen tilt angle in degrees
        tremor_amount: Hand tremor amplitude
        duration: Stroke duration in seconds
        
    Returns:
        Humanized stroke
    """
    # Apply effects in sequence
    stroke = emulate_pressure(stroke, variation=pressure_variation)
    stroke = emulate_tilt(stroke, tilt_angle=tilt_angle)
    stroke = emulate_speed_variation(stroke, duration=duration, speed_curve="ease")
    stroke = add_tremor(stroke, amplitude=tremor_amount)
    
    return stroke
