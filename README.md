# Cerebrum - AI-Driven Art Platform

Cerebrum is an AI-driven art platform that mimics the iterative creative workflow of a human artist. Unlike traditional AI art generators that hallucinate complete images, Cerebrum separates perceptual analysis (Vision), execution (Motor), and task planning (Brain) into modular components to simulate deliberate drawing decisions.

## Project Status

**Current Milestone**: Motor System MVP (Milestone 1) ✓ Complete

### Completed Components

- ✅ **Motor System** - Drawing Control Layer
  - Unified API for drawing operations
  - Krita backend adapter
  - Simulation backend (PIL/Pillow)
  - Stroke processing and path manipulation
  - Human-like stroke emulation
  - Layer and tool management
  - Undo/redo functionality

### Roadmap

- 🔄 **Vision System** - Canvas analysis and feedback (Milestone 2)
- 🔄 **Brain System** - Planning and decision engine (Milestone 3)
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
- [Examples](examples/) - Usage examples
  - `basic_usage.py` - Simple drawing operations
  - `advanced_usage.py` - Advanced features demonstration

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
- **Vision System** (Planned): Analyzes canvas state, detects structure, symmetry, anatomy
- **Brain System** (Planned): Makes decisions, plans corrections, schedules refinements
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
│   └── utils/             # Utilities (path processing, emulation)
├── vision/                # Vision system (planned)
├── brain/                 # Brain system (planned)
├── style_ai/              # Style AI system (planned)
├── examples/              # Usage examples
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── README.md              # This file
```

## Requirements

- Python 3.12+
- Pillow 10.0+ (for simulation backend)
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