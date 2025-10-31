"""
Basic Motor System Usage Example

This example demonstrates the fundamental capabilities of the Motor system:
- Creating a canvas
- Switching tools
- Drawing simple strokes
- Saving the result
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor import MotorInterface, Stroke, StrokePoint, ToolPresets


def main():
    """Run basic motor system demonstration."""
    print("=== Motor System Basic Example ===\n")
    
    # Initialize motor interface with simulation backend
    print("1. Initializing motor interface...")
    motor = MotorInterface(backend="simulation")
    
    # Create a canvas
    print("2. Creating 800x600 canvas...")
    motor.create_canvas(width=800, height=600, name="Basic Example")
    
    # Switch to pencil tool
    print("3. Selecting pencil tool...")
    pencil = ToolPresets.pencil(size=5.0)
    motor.switch_tool(pencil)
    
    # Draw a simple horizontal line
    print("4. Drawing horizontal line...")
    line_points = [
        StrokePoint(x=100, y=300, pressure=0.5),
        StrokePoint(x=200, y=300, pressure=0.8),
        StrokePoint(x=300, y=300, pressure=1.0),
        StrokePoint(x=400, y=300, pressure=0.8),
        StrokePoint(x=500, y=300, pressure=0.5),
    ]
    line_stroke = Stroke(points=line_points)
    motor.draw_stroke(line_stroke)
    
    # Draw a vertical line
    print("5. Drawing vertical line...")
    vertical_points = [
        StrokePoint(x=300, y=100, pressure=0.7),
        StrokePoint(x=300, y=200, pressure=0.9),
        StrokePoint(x=300, y=300, pressure=1.0),
        StrokePoint(x=300, y=400, pressure=0.9),
        StrokePoint(x=300, y=500, pressure=0.7),
    ]
    vertical_stroke = Stroke(points=vertical_points)
    motor.draw_stroke(vertical_stroke)
    
    # Switch to brush and draw a curve
    print("6. Switching to brush and drawing curve...")
    brush = ToolPresets.brush(size=15.0)
    motor.switch_tool(brush)
    
    curve_points = []
    for i in range(50):
        t = i / 49
        x = 100 + t * 600
        y = 300 + 100 * (t * (1 - t) * 4)  # Parabolic curve
        pressure = 0.5 + 0.5 * (1 - abs(2 * t - 1))  # Peak in middle
        curve_points.append(StrokePoint(x=x, y=y, pressure=pressure))
    
    curve_stroke = Stroke(points=curve_points)
    motor.draw_stroke(curve_stroke)
    
    # Save the result
    output_path = Path(__file__).parent / "output" / "basic_example.png"
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"7. Saving to {output_path}...")
    motor.save(output_path)
    
    # Cleanup
    motor.close()
    
    print("\n✓ Basic example complete!")
    print(f"  Output saved to: {output_path}")


if __name__ == "__main__":
    main()
