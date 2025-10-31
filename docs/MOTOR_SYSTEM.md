# Motor System Documentation

## Overview

The Motor System is the drawing control layer of the Cerebrum AI-driven art platform. It provides a unified interface for controlling drawing applications, mimicking the motor control of a human artist's hand.

## Architecture

The Motor System consists of several key components:

### Core Components

- **MotorInterface**: Main API for drawing operations
- **Stroke**: Represents a continuous drawing action with multiple points
- **Tool**: Encapsulates drawing tool configuration (pencil, brush, eraser, etc.)
- **Canvas**: Manages the drawing surface and layers

### Backend Adapters

- **KritaBackend**: Connects to Krita via Python API
- **SimulationBackend**: Standalone implementation using PIL/Pillow

### Utilities

- **Path Processing**: SVG parsing, bezier sampling, path smoothing
- **Stroke Emulation**: Pressure, tilt, timing, and tremor simulation

## Installation

### Requirements

```bash
pip install Pillow>=10.0.0
```

For Krita integration (optional):
- Krita 5.0+ with Python plugin enabled

### Basic Setup

```python
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint

# Initialize with simulation backend
motor = MotorInterface(backend="simulation")

# Or use Krita backend (requires Krita running)
# motor = MotorInterface(backend="krita")
```

## Quick Start

### Creating a Canvas

```python
# Create 800x600 canvas with white background
motor.create_canvas(
    width=800,
    height=600,
    name="My Drawing",
    background_color=(255, 255, 255, 255),  # RGBA
    dpi=300
)
```

### Drawing Strokes

```python
# Select a tool
pencil = ToolPresets.pencil(size=5.0)
motor.switch_tool(pencil)

# Create a stroke with points
points = [
    StrokePoint(x=100, y=100, pressure=0.5),
    StrokePoint(x=200, y=150, pressure=0.8),
    StrokePoint(x=300, y=100, pressure=0.5),
]
stroke = Stroke(points=points)

# Draw the stroke
motor.draw_stroke(stroke)
```

### Working with Tools

```python
# Use preset tools
pencil = ToolPresets.pencil(size=3.0)
pen = ToolPresets.pen(size=5.0)
brush = ToolPresets.brush(size=20.0)
eraser = ToolPresets.eraser(size=15.0)
airbrush = ToolPresets.airbrush(size=30.0)

# Customize brush settings
motor.set_brush(
    size=10.0,
    opacity=0.8,
    hardness=0.6,
    spacing=0.1
)
```

### Managing Layers

```python
# Create layers
sketch_layer = motor.create_layer("Sketch")
detail_layer = motor.create_layer("Details")

# Switch active layer
motor.set_active_layer(sketch_layer.layer_id)

# Delete layer
motor.delete_layer(sketch_layer.layer_id)
```

### Undo/Redo

```python
# Undo last operation
motor.undo()

# Redo
motor.redo()

# Get history
history = motor.get_history()
```

### Saving

```python
# Save as PNG
motor.save("output.png")

# Save as JPEG
motor.save("output.jpg", format="jpeg")

# Export with options
motor.export("output.png", format="png", quality=95)
```

## Advanced Features

### SVG Path Import

```python
from motor.utils.path_processing import svg_to_stroke

# Convert SVG path to stroke
svg_path = "M 10,10 L 100,100 C 150,150 200,150 250,100"
stroke = svg_to_stroke(svg_path, sample_rate=50)
motor.draw_stroke(stroke)
```

### Stroke Humanization

```python
from motor.utils.stroke_emulation import humanize_stroke

# Add realistic human variations
humanized = humanize_stroke(
    stroke,
    pressure_variation=0.2,  # Pressure variance
    tilt_angle=30.0,         # Pen tilt
    tremor_amount=0.5,       # Hand shake
    duration=1.0             # Stroke duration
)
motor.draw_stroke(humanized)
```

### Path Smoothing

```python
from motor.utils.path_processing import smooth_path

# Smooth a stroke path
smoothed_points = smooth_path(stroke.points, smoothing=0.5)
smooth_stroke = Stroke(points=smoothed_points)
motor.draw_stroke(smooth_stroke)
```

### Pressure Emulation

```python
from motor.utils.stroke_emulation import emulate_pressure

# Add pressure variation
stroke_with_pressure = emulate_pressure(
    stroke,
    base_pressure=0.7,
    variation=0.2,
    fade_in=True,
    fade_out=True
)
motor.draw_stroke(stroke_with_pressure)
```

### Tilt Simulation

```python
from motor.utils.stroke_emulation import emulate_tilt

# Add pen tilt
tilted_stroke = emulate_tilt(
    stroke,
    tilt_angle=45.0,      # Angle from vertical
    tilt_direction=0.0,   # Direction
    variation=5.0         # Random variation
)
motor.draw_stroke(tilted_stroke)
```

## StrokePoint Attributes

Each point in a stroke contains:

- `x`, `y`: Position (normalized 0-1 or absolute pixels)
- `pressure`: Pen pressure (0.0-1.0)
- `tilt_x`, `tilt_y`: Pen tilt (-1.0 to 1.0)
- `rotation`: Pen rotation (0-360 degrees)
- `timestamp`: Time offset from stroke start (seconds)
- `velocity`: Stroke velocity (pixels/second)

## Tool Configuration

### BrushConfig Parameters

- `size`: Brush size in pixels
- `opacity`: Brush opacity (0.0-1.0)
- `flow`: Paint flow rate (0.0-1.0)
- `hardness`: Edge hardness (0.0-1.0)
- `spacing`: Spacing between dabs (0.0-1.0)
- `angle`: Brush rotation angle (degrees)
- `pressure_size`: Use pressure for size
- `pressure_opacity`: Use pressure for opacity
- `pressure_hardness`: Use pressure for hardness
- `tilt_angle`: Use tilt for angle
- `blend_mode`: Blending mode
- `anti_alias`: Enable anti-aliasing
- `smoothing`: Stroke smoothing (0.0-1.0)

## Backend Selection

### Simulation Backend

Best for:
- Testing and development
- Batch processing
- Headless operation
- Quick prototyping

Limitations:
- Simpler rendering
- No advanced brush engines
- Basic blending modes

### Krita Backend

Best for:
- Professional quality output
- Advanced brush engines
- Complex blending
- Plugin integration

Requirements:
- Krita must be running
- Python plugin enabled
- Krita API available

## Integration with Vision and Brain

The Motor system is designed to interface with future Vision and Brain components:

### Vision → Motor
Vision analyzes the canvas and provides feedback to Brain, which then issues drawing commands to Motor.

### Brain → Motor
Brain decides what to draw and issues high-level commands that Motor executes.

### Motor → Canvas
Motor translates commands into actual drawing operations on the canvas.

## Example Workflow

```python
# 1. Initialize system
motor = MotorInterface(backend="simulation")
motor.create_canvas(1024, 1024)

# 2. Sketch phase (light, gestural)
motor.switch_tool(ToolPresets.pencil(size=2.0))
sketch_layer = motor.create_layer("Sketch")
# ... draw construction lines ...

# 3. Structure phase (defined shapes)
motor.switch_tool(ToolPresets.pen(size=4.0))
structure_layer = motor.create_layer("Structure")
# ... draw main forms ...

# 4. Detail phase (refinement)
motor.switch_tool(ToolPresets.brush(size=3.0))
detail_layer = motor.create_layer("Details")
# ... add details ...

# 5. Save result
motor.save("final_output.png")
motor.close()
```

## Error Handling

```python
try:
    motor = MotorInterface(backend="krita")
    motor.create_canvas(800, 600)
    # ... drawing operations ...
except Exception as e:
    print(f"Error: {e}")
    # Fallback to simulation
    motor = MotorInterface(backend="simulation")
```

## Logging

The Motor system uses Python's logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger("motor")
logger.setLevel(logging.INFO)
```

## Best Practices

1. **Always close the motor interface** when done:
   ```python
   motor.close()
   ```

2. **Use appropriate tool presets** for different drawing styles

3. **Humanize strokes** for more natural appearance

4. **Work with layers** to organize drawing stages

5. **Test with simulation backend** before using Krita

6. **Save regularly** to avoid data loss

7. **Clear history** for long-running sessions:
   ```python
   motor.clear_history()
   ```

## Performance Considerations

- **Stroke complexity**: More points = slower rendering
- **Layer count**: Many layers increase memory usage
- **History size**: Large undo stack uses memory
- **Backend choice**: Simulation is faster for simple operations

## Troubleshooting

### "Krita API not available"
- Ensure Krita is running
- Enable Python plugin in Krita settings
- Run script from within Krita

### "PIL/Pillow is required"
- Install: `pip install Pillow`

### Strokes not appearing
- Check canvas is created
- Verify tool is set
- Ensure points are within canvas bounds
- Check layer visibility

### Poor performance
- Reduce stroke point count
- Use stroke resampling
- Clear undo history
- Use appropriate backend

## API Reference

See inline documentation in:
- `motor/core/motor_interface.py`
- `motor/core/stroke.py`
- `motor/core/tool.py`
- `motor/core/canvas.py`

## Contributing

When extending the Motor system:
1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Maintain backend interface compatibility
