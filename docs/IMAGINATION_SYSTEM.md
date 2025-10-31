# Imagination System - Style Suggestion Engine

The Imagination System is the style suggestion engine for the Cerebrum AI art platform. It provides capabilities for analyzing style features, generating stylized references, and suggesting transferable elements — all while following the principle that AI-generated images are inspiration, not final output.

## Overview

The Imagination System enables exploration of alternative artistic directions without blindly copying AI-generated content. It emphasizes:

- **Style Analysis**: Extract and tag style features (line style, contrast, color palette, brushwork, lighting)
- **Reference Generation**: Create stylized variations for inspiration
- **Transferable Elements**: Identify specific elements that can be applied (lighting direction, color temperature, etc.)
- **Region-Specific Generation**: Use masking to explore styles for specific areas

## Architecture

```
imagination/
├── core/
│   ├── style_analyzer.py      # Analyzes style features from images
│   └── reference_generator.py # Generates stylized references
├── models/
│   └── style_data.py          # Data structures for style representation
└── imagination_module.py      # Main API
```

## Key Components

### ImaginationModule

The main interface for the Imagination System.

```python
from imagination import ImaginationModule, GenerationParams

imagination = ImaginationModule(simulation_mode=True)
```

**Parameters:**
- `simulation_mode` (bool): Use simulation instead of real AI models. In simulation mode, style generation uses image processing techniques instead of diffusion models.

### StyleAnalyzer

Analyzes images to extract style features.

```python
from imagination.core import StyleAnalyzer

analyzer = StyleAnalyzer()
style = analyzer.analyze(image, analyze_colors=True, analyze_brushwork=True)
```

**Extracted Features:**
- Line style (smooth, sketchy, angular, flowing, broken, hatched)
- Contrast level (low, medium, high, dramatic)
- Color palette (dominant colors, temperature, saturation)
- Brushwork (stroke visibility, texture, edge softness)
- Lighting (direction, intensity, contrast ratio)
- Form exaggeration (optional)

### ReferenceGenerator

Generates stylized reference images.

```python
from imagination.core import ReferenceGenerator
from imagination.models import GenerationParams

generator = ReferenceGenerator(simulation_mode=True)
params = GenerationParams(strength=0.75, style_prompt="impressionist")
suggestion = generator.generate_stylized_reference(image, params)
```

## Usage Examples

### 1. Analyze Current Style

```python
from imagination import ImaginationModule

imagination = ImaginationModule()

# Analyze an image
style = imagination.tag_style_elements("canvas.png")

print(f"Line style: {style.line_style.value}")
print(f"Contrast: {style.contrast_level.value}")

if style.color_palette:
    print(f"Temperature: {style.color_palette.temperature:.2f}")
    print(f"Dominant colors: {style.color_palette.dominant_colors[:3]}")

if style.brushwork:
    print(f"Stroke visibility: {style.brushwork.stroke_visibility:.2f}")
    print(f"Texture intensity: {style.brushwork.texture_intensity:.2f}")
```

### 2. Generate Stylized Reference

```python
from imagination import ImaginationModule, GenerationParams

imagination = ImaginationModule()

# Create generation parameters
params = GenerationParams(
    strength=0.75,              # How much to alter (0-1)
    style_prompt="oil painting",
    guidance_scale=7.5,
    steps=50,
    seed=42                     # For reproducibility
)

# Generate reference
suggestion = imagination.generate_stylized_reference("canvas.png", params)

print(f"Generated: {suggestion.name}")
print(f"Transferable elements: {suggestion.transferable_elements}")

# Use suggestion.reference_image as inspiration
```

### 3. Get Multiple Style Alternatives

```python
from imagination import ImaginationModule

imagination = ImaginationModule()

# Get 3 style suggestions
suggestions = imagination.suggest_alternative_style(
    "wip.png",
    n_suggestions=3
)

for suggestion in suggestions:
    print(f"\n{suggestion.name}:")
    print(f"  Confidence: {suggestion.confidence:.1%}")
    print(f"  Transferable: {', '.join(suggestion.transferable_elements)}")
    # Display suggestion.reference_image for review
```

### 4. Generate with Region Mask

```python
import numpy as np
from imagination import ImaginationModule, GenerationParams

imagination = ImaginationModule()

# Create mask for specific region
mask = np.zeros((height, width), dtype=np.float32)
mask[100:200, 150:250] = 1.0  # Mark region to restyle

# Generate for masked region only
params = GenerationParams(strength=0.8, style_prompt="watercolor")
result = imagination.generate_with_mask("canvas.png", mask, params)
```

### 5. Extract Transferable Elements

```python
from imagination import ImaginationModule

imagination = ImaginationModule()

# Analyze reference and identify what can be transferred
elements = imagination.extract_transferable_elements(
    "generated_ref.png",
    "my_canvas.png"
)

for element, info in elements.items():
    print(f"{element}:")
    if 'current' in info and 'suggested' in info:
        print(f"  Current: {info['current']:.2f}")
        print(f"  Suggested: {info['suggested']:.2f}")
    print(f"  Confidence: {info['confidence']:.1%}")
```

### 6. Compare Styles

```python
from imagination import ImaginationModule

imagination = ImaginationModule()

similarity = imagination.compare_styles("canvas.png", "reference.png")
print(f"Style similarity: {similarity:.1%}")
```

## Data Structures

### StyleAnalysis

Contains analyzed style features from an image.

```python
@dataclass
class StyleAnalysis:
    line_style: Optional[LineStyle]
    contrast_level: Optional[ContrastLevel]
    color_palette: Optional[ColorPalette]
    brushwork: Optional[BrushworkAnalysis]
    lighting: Optional[LightingAnalysis]
    form_exaggeration: Optional[FormExaggeration]
    confidence: float
    processing_time_ms: float
```

### StyleSuggestion

A suggested style alternative with transferable elements.

```python
@dataclass
class StyleSuggestion:
    name: str
    features: Dict[str, Any]
    transferable_elements: List[str]
    reference_image: Optional[np.ndarray]
    mask: Optional[np.ndarray]
    confidence: float
```

### GenerationParams

Parameters for style generation.

```python
@dataclass
class GenerationParams:
    strength: float = 0.75           # How much to alter (0-1)
    guidance_scale: float = 7.5      # Style adherence (1-20)
    steps: int = 50                  # Diffusion steps
    seed: Optional[int] = None       # Random seed
    mask_region: Optional[Tuple] = None  # (x, y, w, h)
    style_prompt: str = ""           # Text prompt
```

## Design Principles

### 1. AI as Reference, Not Output

Generated images serve as inspiration and reference material. They should be analyzed for transferable elements rather than used directly.

```python
# ✓ Good: Extract transferable elements
elements = imagination.extract_transferable_elements(reference, canvas)
# Apply only relevant elements to your work

# ✗ Bad: Directly copy generated image
# canvas = generated_image  # Don't do this
```

### 2. Structure Before Style

Always ensure structural correctness (anatomy, proportions) before applying stylistic changes.

```python
# Correct workflow:
# 1. Vision system validates structure
# 2. Brain system plans corrections
# 3. Motor system executes corrections
# 4. Imagination suggests style refinements
```

### 3. Traceable Decisions

Every style suggestion includes analysis of what was applied and why.

```python
suggestion = imagination.generate_stylized_reference(canvas, params)

print("Applied features:")
for key, value in suggestion.features.items():
    print(f"  {key}: {value}")

print("\nTransferable elements:")
for element in suggestion.transferable_elements:
    print(f"  - {element}")
```

### 4. Simulation Mode

The module operates in simulation mode by default, using image processing techniques. This ensures functionality without requiring large AI models.

For production use with real models (SDXL, Kandinsky, etc.):

```python
# Future: Integration with real models
imagination = ImaginationModule(simulation_mode=False)
# Would use actual diffusion models for generation
```

## Integration with Other Systems

### With Vision System

```python
from vision import VisionModule
from imagination import ImaginationModule

vision = VisionModule()
imagination = ImaginationModule()

# Analyze canvas structure
analysis = vision.analyze("canvas.png")

# Only proceed with style suggestions if structure is acceptable
if analysis.proportion_metrics.overall_score > 0.7:
    # Structure is good, suggest styles
    suggestions = imagination.suggest_alternative_style("canvas.png")
```

### With Brain System

```python
from brain import BrainModule
from imagination import ImaginationModule

brain = BrainModule()
imagination = ImaginationModule()

# Brain decides when to explore style alternatives
if brain.should_explore_styles():
    suggestions = imagination.suggest_alternative_style("wip.png")
    # Brain evaluates suggestions and decides which to incorporate
```

### With Motor System

```python
from motor import MotorInterface
from imagination import ImaginationModule

motor = MotorInterface(backend="simulation")
imagination = ImaginationModule()

# Get style suggestion
suggestion = imagination.generate_stylized_reference("canvas.png", params)

# Extract color palette for motor to use
if suggestion.transferable_elements and "color_palette" in suggestion.transferable_elements:
    # Analyze the reference for colors
    ref_style = imagination.tag_style_elements(suggestion.reference_image)
    # Use ref_style.color_palette to guide color choices in motor
```

## Performance Considerations

### Style Analysis

- **Fast**: Color palette, contrast, line style (~50-200ms)
- **Medium**: Brushwork, lighting analysis (~500-1000ms)
- **Slow**: Form exaggeration with pose detection (~1-3s)

### Reference Generation

- **Simulation Mode**: Fast (~100-500ms depending on image size)
- **Real Models** (future): Slower (~5-30s depending on model and steps)

### Optimization Tips

```python
# Only analyze needed features
style = imagination.tag_style_elements(
    image,
    analyze_colors=True,
    analyze_brushwork=False,  # Skip if not needed
    analyze_lighting=False,
    analyze_form=False
)

# Use lower strength for faster generation
params = GenerationParams(strength=0.5)  # Faster than 0.9

# Reduce steps in simulation
params = GenerationParams(steps=20)  # Faster than 50
```

## Best Practices

1. **Start with Analysis**: Always analyze current style before generating alternatives
2. **Limit Suggestions**: Generate 2-3 alternatives, not dozens
3. **Selective Transfer**: Only transfer relevant elements, not everything
4. **Validate Structure First**: Ensure anatomy/proportions are correct before styling
5. **Use Masks Wisely**: Focus style exploration on specific regions when appropriate
6. **Document Choices**: Track which elements were transferred and why

## Future Enhancements

The Imagination System is designed to integrate with real AI models:

- **SDXL Integration**: High-quality image-to-image generation
- **Kandinsky Support**: Alternative style generation engine
- **ControlNet**: Structure-preserving style transfer
- **Style Transfer Models**: Neural style transfer networks
- **Custom Model Support**: Plugin architecture for new models

## Troubleshooting

### Issue: Generated references look too different

```python
# Reduce strength
params = GenerationParams(strength=0.5)  # Instead of 0.9
```

### Issue: Not enough style variation

```python
# Increase strength
params = GenerationParams(strength=0.8)  # Instead of 0.5
```

### Issue: Analysis missing features

```python
# Enable all analysis options
style = imagination.tag_style_elements(
    image,
    analyze_colors=True,
    analyze_brushwork=True,
    analyze_lighting=True,
    analyze_form=True  # Enable form analysis
)
```

## API Reference

See the module docstrings for complete API documentation:

```python
help(ImaginationModule)
help(StyleAnalyzer)
help(ReferenceGenerator)
```

## Examples

Run the included examples:

```bash
python examples/imagination_usage.py
```

## Testing

Run the test suite:

```bash
pytest tests/imagination/ -v
```

All 30 imagination tests should pass.
