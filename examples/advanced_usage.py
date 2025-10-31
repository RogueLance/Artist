"""
Advanced Motor System Example

Demonstrates advanced features:
- SVG path import
- Stroke humanization
- Layer management
- Multiple tools
- Undo/redo
"""

import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor import MotorInterface, Stroke, StrokePoint, ToolPresets
from motor.utils.path_processing import svg_to_stroke, smooth_path
from motor.utils.stroke_emulation import humanize_stroke


def create_circle_stroke(center_x, center_y, radius, num_points=100):
    """Create a circular stroke."""
    points = []
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append(StrokePoint(x=x, y=y))
    
    # Close the circle
    points.append(points[0])
    return Stroke(points=points)


def main():
    """Run advanced motor system demonstration."""
    print("=== Motor System Advanced Example ===\n")
    
    # Initialize
    print("1. Initializing motor interface...")
    motor = MotorInterface(backend="simulation")
    
    # Create canvas
    print("2. Creating canvas...")
    motor.create_canvas(width=1000, height=800, name="Advanced Example")
    
    # Create multiple layers
    print("3. Creating layers...")
    sketch_layer = motor.create_layer("Sketch")
    motor.set_active_layer(sketch_layer.layer_id)
    
    # Draw construction circles (light pencil)
    print("4. Drawing construction geometry...")
    pencil = ToolPresets.pencil(size=2.0)
    pencil.color = (200, 200, 200, 128)  # Light gray
    motor.switch_tool(pencil)
    
    # Draw guide circles
    circle1 = create_circle_stroke(300, 400, 150)
    circle1 = humanize_stroke(circle1, tremor_amount=0.3)
    motor.draw_stroke(circle1)
    
    circle2 = create_circle_stroke(700, 400, 150)
    circle2 = humanize_stroke(circle2, tremor_amount=0.3)
    motor.draw_stroke(circle2)
    
    # Create details layer
    print("5. Adding detail layer...")
    detail_layer = motor.create_layer("Details")
    motor.set_active_layer(detail_layer.layer_id)
    
    # Draw with pen tool
    print("6. Drawing refined strokes...")
    pen = ToolPresets.pen(size=4.0)
    pen.color = (0, 0, 0, 255)  # Black
    motor.switch_tool(pen)
    
    # Draw connecting curve between circles
    curve_points = []
    for i in range(50):
        t = i / 49
        x = 300 + t * 400
        y = 400 - 50 * math.sin(t * math.pi)
        curve_points.append(StrokePoint(x=x, y=y))
    
    curve_stroke = Stroke(points=curve_points)
    curve_stroke = humanize_stroke(
        curve_stroke,
        pressure_variation=0.15,
        tilt_angle=35.0,
        tremor_amount=0.5,
        duration=1.5
    )
    motor.draw_stroke(curve_stroke)
    
    # SVG path example
    print("7. Drawing from SVG path...")
    svg_path = "M 450,200 Q 500,150 550,200 T 650,200"
    svg_stroke = svg_to_stroke(svg_path, sample_rate=30)
    svg_stroke = smooth_path(svg_stroke.points, smoothing=0.3)
    svg_stroke = Stroke(points=svg_stroke)
    svg_stroke = humanize_stroke(svg_stroke)
    motor.draw_stroke(svg_stroke)
    
    # Add some brush strokes
    print("8. Adding brush accents...")
    brush = ToolPresets.brush(size=25.0)
    brush.color = (100, 100, 255, 180)  # Blue
    motor.switch_tool(brush)
    
    # Accent stroke
    accent_points = [
        StrokePoint(x=250, y=350),
        StrokePoint(x=350, y=380),
        StrokePoint(x=450, y=370),
    ]
    accent_stroke = Stroke(points=accent_points)
    accent_stroke = humanize_stroke(accent_stroke, pressure_variation=0.3)
    motor.draw_stroke(accent_stroke)
    
    # Demonstrate undo
    print("9. Testing undo...")
    motor.undo()
    print("   Undid last stroke")
    
    # Redo
    print("10. Testing redo...")
    motor.redo()
    print("    Redid stroke")
    
    # Save final result
    output_path = Path(__file__).parent / "output" / "advanced_example.png"
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"11. Saving to {output_path}...")
    motor.save(output_path)
    
    # Cleanup
    motor.close()
    
    print("\n✓ Advanced example complete!")
    print(f"  Output saved to: {output_path}")
    print(f"  Layers created: {len(motor.get_canvas().layers)}")


if __name__ == "__main__":
    main()
