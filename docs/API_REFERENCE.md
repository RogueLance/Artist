# Motor System API Reference

## Core Classes

### MotorInterface

Main interface for drawing operations.

#### Constructor

```python
MotorInterface(backend: Union[str, BackendInterface] = "simulation")
```

**Parameters:**
- `backend`: Backend to use ("krita", "simulation", or BackendInterface instance)

#### Methods

##### create_canvas
```python
create_canvas(
    width: int,
    height: int,
    name: str = "Untitled",
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    dpi: int = 300
) -> Canvas
```

Create a new canvas.

**Returns:** Canvas object

##### draw_stroke
```python
draw_stroke(stroke: Stroke) -> bool
```

Draw a stroke on the canvas.

**Returns:** True if successful

##### erase_stroke
```python
erase_stroke(stroke: Stroke) -> bool
```

Erase along a stroke path.

**Returns:** True if successful

##### switch_tool
```python
switch_tool(tool: Tool) -> None
```

Switch to a different drawing tool.

##### set_brush
```python
set_brush(
    size: Optional[float] = None,
    opacity: Optional[float] = None,
    hardness: Optional[float] = None,
    **kwargs
) -> None
```

Update brush configuration.

##### create_layer
```python
create_layer(name: str, position: Optional[int] = None) -> Optional[Layer]
```

Create a new layer.

**Returns:** The created Layer object

##### delete_layer
```python
delete_layer(layer_id: str) -> bool
```

Delete a layer by ID.

**Returns:** True if successful

##### set_active_layer
```python
set_active_layer(layer_id: str) -> bool
```

Set the active drawing layer.

**Returns:** True if successful

##### undo
```python
undo() -> bool
```

Undo the last operation.

**Returns:** True if successful

##### redo
```python
redo() -> bool
```

Redo the last undone operation.

**Returns:** True if successful

##### save
```python
save(filepath: Union[str, Path], format: Optional[str] = None) -> bool
```

Save the canvas to a file.

**Returns:** True if successful

##### close
```python
close() -> None
```

Close the motor interface and cleanup resources.

---

### Stroke

Represents a complete stroke with multiple points.

#### Constructor

```python
Stroke(
    points: List[StrokePoint] = [],
    stroke_type: StrokeType = StrokeType.DRAW,
    tool_id: Optional[str] = None,
    layer_id: Optional[str] = None,
    color: Optional[Tuple[int, int, int, int]] = None,
    metadata: dict = {}
)
```

#### Methods

##### add_point
```python
add_point(point: StrokePoint) -> None
```

Add a point to the stroke.

##### get_bounds
```python
get_bounds() -> Tuple[float, float, float, float]
```

Get bounding box of the stroke.

**Returns:** (min_x, min_y, max_x, max_y)

##### length
```python
length() -> float
```

Calculate total length of the stroke.

##### resample
```python
resample(target_points: int) -> Stroke
```

Resample stroke to have a specific number of points.

##### to_dict / from_dict
```python
to_dict() -> dict
from_dict(data: dict) -> Stroke
```

Serialize/deserialize stroke.

---

### StrokePoint

A single point in a stroke.

#### Constructor

```python
StrokePoint(
    x: float,
    y: float,
    pressure: float = 1.0,
    tilt_x: float = 0.0,
    tilt_y: float = 0.0,
    rotation: float = 0.0,
    timestamp: float = 0.0,
    velocity: float = 0.0
)
```

#### Attributes

- `x`: X coordinate
- `y`: Y coordinate
- `pressure`: Pen pressure (0.0-1.0)
- `tilt_x`: Pen tilt in X direction (-1.0 to 1.0)
- `tilt_y`: Pen tilt in Y direction (-1.0 to 1.0)
- `rotation`: Pen rotation (0-360 degrees)
- `timestamp`: Time offset from stroke start (seconds)
- `velocity`: Stroke velocity (pixels/second)

---

### Tool

Represents a drawing tool with its configuration.

#### Constructor

```python
Tool(
    tool_type: ToolType,
    config: BrushConfig = BrushConfig(),
    name: Optional[str] = None,
    tool_id: Optional[str] = None,
    color: tuple = (0, 0, 0, 255)
)
```

---

### ToolPresets

Factory class for common tool presets.

#### Static Methods

##### pencil
```python
ToolPresets.pencil(size: float = 2.0) -> Tool
```

##### pen
```python
ToolPresets.pen(size: float = 3.0) -> Tool
```

##### brush
```python
ToolPresets.brush(size: float = 20.0) -> Tool
```

##### eraser
```python
ToolPresets.eraser(size: float = 20.0) -> Tool
```

##### airbrush
```python
ToolPresets.airbrush(size: float = 30.0) -> Tool
```

---

### Canvas

Represents the drawing canvas.

#### Constructor

```python
Canvas(
    width: int,
    height: int,
    canvas_id: str = auto_generated,
    name: str = "Untitled",
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    dpi: int = 300,
    layers: List[Layer] = [],
    active_layer_id: Optional[str] = None,
    metadata: Dict[str, Any] = {}
)
```

#### Methods

##### add_layer
```python
add_layer(name: str, position: Optional[int] = None) -> Layer
```

##### remove_layer
```python
remove_layer(layer_id: str) -> bool
```

##### get_layer
```python
get_layer(layer_id: str) -> Optional[Layer]
```

##### set_active_layer
```python
set_active_layer(layer_id: str) -> bool
```

---

## Utility Functions

### Path Processing

#### svg_to_stroke
```python
svg_to_stroke(svg_path: str, sample_rate: int = 50) -> Stroke
```

Convert an SVG path string to a Stroke.

#### bezier_to_points
```python
bezier_to_points(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    num_points: int = 50
) -> List[StrokePoint]
```

Sample points from a cubic Bezier curve.

#### smooth_path
```python
smooth_path(
    points: List[StrokePoint],
    smoothing: float = 0.5
) -> List[StrokePoint]
```

Smooth a path using moving average.

#### resample_path
```python
resample_path(
    points: List[StrokePoint],
    target_spacing: float
) -> List[StrokePoint]
```

Resample path to have uniform spacing between points.

---

### Stroke Emulation

#### emulate_pressure
```python
emulate_pressure(
    stroke: Stroke,
    base_pressure: float = 0.7,
    variation: float = 0.2,
    fade_in: bool = True,
    fade_out: bool = True
) -> Stroke
```

Add realistic pressure variation to a stroke.

#### emulate_tilt
```python
emulate_tilt(
    stroke: Stroke,
    tilt_angle: float = 45.0,
    tilt_direction: float = 0.0,
    variation: float = 5.0
) -> Stroke
```

Add pen tilt to a stroke.

#### emulate_speed_variation
```python
emulate_speed_variation(
    stroke: Stroke,
    duration: float = 1.0,
    speed_curve: str = "ease"
) -> Stroke
```

Add timing variation to simulate drawing speed.

**speed_curve options:** "linear", "ease", "ease-in", "ease-out"

#### add_tremor
```python
add_tremor(
    stroke: Stroke,
    amplitude: float = 1.0,
    frequency: float = 10.0
) -> Stroke
```

Add hand tremor to a stroke for realism.

#### humanize_stroke
```python
humanize_stroke(
    stroke: Stroke,
    pressure_variation: float = 0.2,
    tilt_angle: float = 30.0,
    tremor_amount: float = 0.5,
    duration: float = 1.0
) -> Stroke
```

Apply a combination of humanizing effects to a stroke.

---

## Enumerations

### ToolType

```python
class ToolType(Enum):
    PENCIL = "pencil"
    PEN = "pen"
    BRUSH = "brush"
    AIRBRUSH = "airbrush"
    ERASER = "eraser"
    SMUDGE = "smudge"
    FILL = "fill"
    EYEDROPPER = "eyedropper"
```

### StrokeType

```python
class StrokeType(Enum):
    DRAW = "draw"
    ERASE = "erase"
```

### BlendMode

```python
class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    ADD = "add"
    SUBTRACT = "subtract"
    ERASE = "erase"
```

---

## Backend Interfaces

### BackendInterface (Abstract)

Base class for all backend implementations.

#### Abstract Methods

- `create_canvas(width, height, background_color) -> bool`
- `set_tool(tool) -> bool`
- `draw_stroke(stroke) -> bool`
- `erase_stroke(stroke) -> bool`
- `clear_canvas() -> bool`
- `create_layer(layer) -> bool`
- `delete_layer(layer_id) -> bool`
- `set_active_layer(layer_id) -> bool`
- `undo() -> bool`
- `redo() -> bool`
- `save(filepath, format) -> bool`
- `close() -> None`

### SimulationBackend

Standalone backend using PIL/Pillow.

### KritaBackend

Backend for Krita digital painting application.

---

## Complete Example

```python
from motor import (
    MotorInterface,
    Stroke,
    StrokePoint,
    ToolPresets
)
from motor.utils.path_processing import svg_to_stroke
from motor.utils.stroke_emulation import humanize_stroke

# Initialize
motor = MotorInterface(backend="simulation")
motor.create_canvas(1024, 768)

# Create layers
sketch_layer = motor.create_layer("Sketch")
motor.set_active_layer(sketch_layer.layer_id)

# Draw with pencil
motor.switch_tool(ToolPresets.pencil(size=3.0))

# Create and humanize stroke
points = [
    StrokePoint(x=100, y=100),
    StrokePoint(x=200, y=150),
    StrokePoint(x=300, y=100),
]
stroke = Stroke(points=points)
stroke = humanize_stroke(stroke)

# Draw
motor.draw_stroke(stroke)

# Import SVG
svg_stroke = svg_to_stroke("M 100,200 L 300,200")
motor.draw_stroke(svg_stroke)

# Save
motor.save("output.png")
motor.close()
```
