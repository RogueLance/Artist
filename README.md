# Cerebrum - AI-Driven Art Platform

Cerebrum is an AI-driven art platform that mimics the iterative creative workflow of a human artist. Unlike traditional AI art generators that hallucinate complete images, Cerebrum separates perceptual analysis (Vision), execution (Motor), and task planning (Brain) into modular components to simulate deliberate drawing decisions.

## Project Status

**Current Milestone**: Brain System MVP (Milestone 3) ✓ Complete

### Completed Components

- ✅ **Motor System** - Drawing Control Layer (31 tests)
  - Unified API for drawing operations
  - Krita backend adapter
  - Simulation backend (PIL/Pillow)
  - Stroke processing and path manipulation
  - Human-like stroke emulation
  - Layer and tool management
  - Undo/redo functionality

- ✅ **Vision System** - Canvas Analysis Engine (32 tests)
  - Pose detection using MediaPipe
  - Face and hand landmark detection
  - Canvas state analysis
  - Reference comparison
  - Pose error detection
  - Proportion and symmetry analysis
  - Edge alignment metrics

- ✅ **Brain System** - Planning and Decision Making (33 tests)
  - Task management and prioritization
  - Vision feedback interpretation
  - Action plan generation
  - Result evaluation and retry logic
  - Motor System integration
  - Iterative refinement workflow
  - State tracking and history

### Roadmap

- 🔄 **Style AI** - Style suggestion and reference (Milestone 4)
- 🔄 **Integration** - Full system integration (Milestone 5)

## Motor System

The Motor System is the drawing control layer that allows the AI to execute drawing operations on a canvas. It provides a unified interface for controlling drawing applications like Krita or using standalone simulation.

### Features

- **Unified Drawing API**: Abstract interface for drawing operations
- **Multiple Backends**: Support for Krita and standalone simulation
- **Stroke Processing**: SVG import, Bezier sampling, path smoothing
- **Human Emulation**: Pressure, tilt, timing, and tremor simulation
- **Layer Management**: Multi-layer canvas with blending modes
- **Tool System**: Configurable brushes, pens, erasers, airbrushes
- **Undo/Redo**: Full history management
- **Export**: PNG, JPEG, and other formats

### Quick Start

```python
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint

# Initialize motor interface
motor = MotorInterface(backend="simulation")

# Create canvas
motor.create_canvas(width=800, height=600)

# Select tool
motor.switch_tool(ToolPresets.pencil(size=5.0))

# Draw a stroke
points = [
    StrokePoint(x=100, y=100, pressure=0.5),
    StrokePoint(x=200, y=150, pressure=0.8),
    StrokePoint(x=300, y=100, pressure=0.5),
]
stroke = Stroke(points=points)
motor.draw_stroke(stroke)

# Save result
motor.save("output.png")
motor.close()
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run examples
python examples/basic_usage.py
python examples/advanced_usage.py

# Run tests
pip install pytest pytest-cov
pytest tests/
```

### Documentation

- [Motor System Documentation](docs/MOTOR_SYSTEM.md) - Complete API reference and guide
- [Vision System Documentation](docs/VISION_SYSTEM.md) - Canvas analysis and perception
- [Examples](examples/) - Usage examples
  - `basic_usage.py` - Simple drawing operations
  - `advanced_usage.py` - Advanced features demonstration

## Vision System

The Vision System provides perception capabilities for analyzing canvas state, detecting poses and anatomy, and comparing to reference images.

### Features

- **Pose Detection**: MediaPipe-based body pose estimation (33 keypoints)
- **Face Detection**: 468 facial landmarks for detailed analysis
- **Hand Detection**: 21 landmarks per hand, multi-hand support
- **Canvas Analysis**: Silhouette extraction, edge detection
- **Comparison Metrics**: Pose differences, proportions, symmetry, alignment
- **Error Detection**: Automatic identification of pose and anatomy issues
- **Refinement Guidance**: Highlighting specific areas needing improvement

### Quick Start

```python
from vision import VisionModule

# Initialize vision module
vision = VisionModule()

# Analyze canvas state
result = vision.analyze("canvas.png")

if result.has_pose():
    print(f"Detected {len(result.pose.keypoints)} keypoints")
    print(f"Proportion score: {result.proportion_metrics.overall_score:.2f}")

# Compare to reference
comparison = vision.compare_to("canvas.png", "reference.png")
print(f"Similarity: {comparison.overall_similarity:.1%}")

# Get pose errors
errors = vision.detect_pose_errors("canvas.png", "reference.png")
for error in errors:
    print(f"- {error}")

# Get areas to refine
areas = vision.highlight_areas_needing_refinement("canvas.png", "reference.png")
for area in areas:
    print(f"Fix {area['type']} at region {area['region']}")

vision.close()
```

## Brain System

The Brain System provides the central decision-making capabilities for planning and executing artistic corrections based on vision feedback.

### Features

- **Task Management**: Create, prioritize, and track tasks
- **Vision Interpretation**: Translate vision feedback into actionable plans
- **Action Planning**: Generate concrete drawing actions for tasks
- **Result Evaluation**: Assess execution success and schedule retries
- **Motor Integration**: Delegate drawing actions to Motor System
- **Iterative Refinement**: Support multi-iteration improvement cycles
- **State Tracking**: Maintain goals, context, and execution history

### Quick Start

```python
from brain import BrainModule
from vision import VisionModule
from motor import MotorInterface

# Initialize systems
brain = BrainModule()
vision = VisionModule()
motor = MotorInterface(backend="simulation")

# Set artistic goal
brain.set_goal("Draw an accurate human figure")

# Create and analyze canvas
motor.create_canvas(800, 600)
# ... draw initial sketch ...
motor.save("canvas.png")

# Analyze with vision
vision_data = vision.analyze("canvas.png")

# Plan corrections
tasks = brain.plan_next_action(vision_data)

# Execute tasks
for task in tasks:
    plan = brain.get_action_plan(task)
    for action in plan.actions:
        brain.delegate_to_motor(action, motor)
    
    # Evaluate result
    result = brain.evaluate_result(task, vision_before, vision_after)
    print(f"Task result: {result.value}")

brain.close()
vision.close()
motor.close()
```

### Integration with Motor System

```python
from motor import MotorInterface
from vision import VisionModule

# Create systems
motor = MotorInterface(backend="simulation")
vision = VisionModule()

# Draw on canvas
motor.create_canvas(800, 600)
# ... draw strokes ...
motor.save("canvas.png")

# Analyze and compare
result = vision.analyze("canvas.png")
comparison = vision.compare_to("canvas.png", "reference.png")

# Use analysis to guide refinement
areas = vision.highlight_areas_needing_refinement("canvas.png", "reference.png")
# ... adjust drawing based on feedback ...
```

## Architecture

Cerebrum follows a modular architecture inspired by human artistic process:

```
┌─────────────────────────────────────────┐
│              Brain System               │
│     (Planning & Decision Making)        │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
┌─────▼─────┐    ┌────▼──────┐
│  Vision   │◄───┤   Motor   │
│  System   │    │  System   │
│           │    │           │
│ Canvas    │    │ Drawing   │
│ Analysis  │    │ Control   │
└───────────┘    └─────┬─────┘
                       │
                ┌──────▼──────┐
                │   Canvas    │
                │  (Krita/    │
                │  Simulation)│
                └─────────────┘
```

### Component Roles

- **Motor System**: Executes drawing commands (strokes, tool changes, etc.)
- **Vision System**: Analyzes canvas state, detects poses, compares to references
- **Brain System**: Makes decisions, plans corrections, schedules refinements
- **Style AI** (Planned): Provides style suggestions and reference imagery

## Design Principles

Cerebrum is designed around these core principles:

1. **Traceable Drawing Logic**: Every stroke is deliberate and intentional
2. **Structural Correctness First**: Anatomy and structure before style
3. **Iterative Refinement**: Gesture → Structure → Detail → Stylization
4. **AI as Reference**: Generated images are inspiration, not output
5. **Modular Architecture**: Clear separation of concerns
6. **Human-like Behavior**: Simulates natural artist workflow

## Project Structure

```
Artist/
├── motor/                  # Motor system (drawing control)
│   ├── core/              # Core classes (interface, stroke, tool, canvas)
│   ├── backends/          # Backend adapters (Krita, simulation)
│   ├── utils/             # Utilities (path processing, emulation)
│   └── config.py          # Configuration
├── vision/                # Vision system (canvas analysis)
│   ├── core/             # Core components (detectors, comparator)
│   ├── models/           # Data structures (poses, landmarks, metrics)
│   ├── utils/            # Utilities (image, geometry, visualization)
│   └── vision_module.py  # Main API
├── brain/                 # Brain system (planning & decision-making)
│   ├── core/             # Core components (planner, task manager, state tracker)
│   ├── models/           # Data structures (tasks, action plans, state)
│   └── brain_module.py   # Main API
├── tests/
│   ├── motor/            # Motor system tests (31 tests)
│   ├── vision/           # Vision system tests (32 tests)
│   └── brain/            # Brain system tests (33 tests)
├── examples/             # Usage examples
├── docs/                 # Documentation
│   ├── MOTOR_SYSTEM.md
│   ├── VISION_SYSTEM.md
│   └── BRAIN_SYSTEM.md
├── requirements.txt
└── setup.py
```

## Requirements

- Python 3.12+
- Pillow 10.0+ (for simulation backend)
- OpenCV 4.8+ (for vision system)
- MediaPipe 0.10+ (for pose/landmark detection)
- NumPy 1.24+ (for numerical operations)
- Krita 5.0+ (optional, for Krita backend)

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=motor --cov-report=html
```

### Adding New Features

1. Implement in appropriate module (motor/vision/brain)
2. Add tests in `tests/`
3. Update documentation in `docs/`
4. Add examples if applicable

## Contributing

Contributions are welcome! Please ensure:

1. Code follows existing style and structure
2. All tests pass
3. New features include tests
4. Documentation is updated

## License

MIT License - See LICENSE file for details

## Acknowledgments

This project is inspired by the need for more deliberate, traceable AI art generation that respects artistic process and structural correctness.