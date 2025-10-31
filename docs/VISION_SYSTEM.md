# Vision System Documentation

## Overview

The Vision System is Milestone 2 of the Cerebrum AI-driven art platform. It provides perception capabilities for analyzing canvas state, detecting poses and anatomy, comparing to reference images, and identifying areas needing refinement.

## Architecture

The Vision System follows a modular architecture similar to the Motor System:

```
vision/
├── __init__.py                 # Main package exports
├── vision_module.py            # Primary API
├── core/                       # Core components
│   ├── image_processor.py      # Image loading and preprocessing
│   ├── pose_detector.py        # Pose detection using MediaPipe
│   ├── landmark_detector.py    # Face and hand detection
│   └── comparator.py           # Comparison metrics
├── models/                     # Data structures
│   ├── analysis_result.py      # Analysis results
│   ├── pose_data.py            # Pose representations
│   ├── landmarks.py            # Landmark data
│   └── comparison_metrics.py   # Metric data structures
└── utils/                      # Utility functions
    ├── image_utils.py          # Image utilities
    ├── geometry.py             # Geometric calculations
    └── visualization.py        # Visualization helpers
```

## Key Components

### VisionModule

The main API for vision analysis. Provides high-level methods for:

- **analyze()**: Analyze canvas state and extract features
- **compare_to()**: Compare canvas to reference image
- **detect_pose_errors()**: Find pose/anatomy issues
- **highlight_areas_needing_refinement()**: Identify areas to improve

### Core Components

#### ImageProcessor
Handles image loading from various sources (file paths, PIL Images, numpy arrays) and preprocessing operations:
- RGB/BGR conversion
- Grayscale conversion
- Resizing with aspect ratio preservation
- Silhouette extraction
- Edge detection using Canny algorithm

#### PoseDetector
Uses MediaPipe Pose to detect human body poses:
- Detects 33 body landmarks
- Returns structured PoseData with keypoints
- Visualizes pose skeleton on images
- Calculates confidence scores

#### LandmarkDetector
Uses MediaPipe for fine-grained feature detection:
- Face detection (468 landmarks)
- Hand detection (21 landmarks per hand)
- Supports multiple hands
- Returns structured landmark data

#### Comparator
Provides comparison and analysis metrics:
- Pose comparison (keypoint differences, angle differences)
- Proportion analysis (body ratios, anatomical correctness)
- Symmetry analysis (bilateral symmetry)
- Edge alignment (overlap, misalignment heatmaps)

## Data Models

### PoseData
Represents a complete pose with keypoints:
```python
pose = PoseData(
    keypoints=[
        PoseKeypoint("nose", x=0.5, y=0.3, confidence=0.9),
        PoseKeypoint("left_shoulder", x=0.4, y=0.5, confidence=0.85),
        # ...
    ],
    confidence=0.87,
    image_width=640,
    image_height=480
)
```

### AnalysisResult
Contains all analysis results for a single image:
```python
result = AnalysisResult(
    pose=pose_data,
    face_landmarks=face_landmarks,
    hand_landmarks=[hand1, hand2],
    silhouette=mask_array,
    edges=edge_array,
    proportion_metrics=proportions,
    symmetry_metrics=symmetry
)
```

### ComparisonResult
Contains comparison metrics between two images:
```python
comparison = ComparisonResult(
    pose_metrics=pose_comparison,
    proportion_metrics=proportions,
    symmetry_metrics=symmetry,
    alignment_metrics=alignment,
    overall_similarity=0.75,
    pose_errors=["left_shoulder differs by 25%"],
    areas_needing_refinement=[region1, region2]
)
```

## Usage Examples

### Basic Analysis

```python
from vision import VisionModule

# Initialize
vision = VisionModule()

# Analyze an image
result = vision.analyze("canvas.png")

# Check what was detected
if result.has_pose():
    print(f"Detected {len(result.pose.keypoints)} keypoints")
    print(f"Confidence: {result.pose.confidence:.2f}")

if result.has_face():
    print(f"Detected face with {len(result.face_landmarks.landmarks)} landmarks")

# Access metrics
if result.proportion_metrics:
    print(f"Proportion score: {result.proportion_metrics.overall_score:.2f}")
    for issue in result.proportion_metrics.issues:
        print(f"- {issue}")
```

### Comparing to Reference

```python
# Compare canvas to reference
comparison = vision.compare_to("canvas.png", "reference.png")

# Check similarity
print(f"Similarity: {comparison.overall_similarity:.1%}")
print(f"Confidence: {comparison.confidence:.1%}")

# Get pose errors
for error in comparison.pose_errors:
    print(f"- {error}")

# Get areas needing work
for area in comparison.areas_needing_refinement:
    print(f"- {area['type']} at {area['region']}")
```

### Detecting Errors

```python
# Detect errors in canvas
errors = vision.detect_pose_errors("canvas.png", "reference.png")

for error in errors:
    print(f"Issue: {error}")
```

### Highlighting Problem Areas

```python
# Get specific areas to refine
areas = vision.highlight_areas_needing_refinement("canvas.png", "reference.png")

for area in areas:
    print(f"Type: {area['type']}")
    print(f"Region: {area['region']}")
    print(f"Severity: {area['severity']}")
```

### Working with Analysis Results

```python
# Analyze image
result = vision.analyze("drawing.png")

# Get pose keypoints
if result.pose:
    for kp in result.pose.keypoints:
        print(f"{kp.name}: ({kp.x:.2f}, {kp.y:.2f}) conf={kp.confidence:.2f}")

# Check proportions
if result.proportion_metrics:
    ratios = result.proportion_metrics.body_ratios
    for name, ratio in ratios.items():
        print(f"{name}: {ratio:.3f}")

# Check symmetry
if result.symmetry_metrics:
    print(f"Symmetry score: {result.symmetry_metrics.symmetry_score:.2f}")
    for feature in result.symmetry_metrics.asymmetric_features:
        print(f"Asymmetric: {feature}")
```

## Integration with Motor System

The Vision System integrates seamlessly with the Motor System:

```python
from motor import MotorInterface
from vision import VisionModule

# Create systems
motor = MotorInterface(backend="simulation")
vision = VisionModule()

# Create and draw on canvas
motor.create_canvas(800, 600)
# ... draw strokes ...

# Save canvas state
motor.save("canvas.png")

# Analyze what was drawn
result = vision.analyze("canvas.png")

# Compare to target
comparison = vision.compare_to("canvas.png", "reference.png")

# Get areas to fix
areas = vision.highlight_areas_needing_refinement("canvas.png", "reference.png")
```

## Configuration

### VisionModule Options

```python
vision = VisionModule(
    enable_pose=True,          # Enable pose detection
    enable_face=True,          # Enable face detection
    enable_hands=True,         # Enable hand detection
    min_detection_confidence=0.5  # Minimum confidence threshold
)
```

### Analysis Options

```python
result = vision.analyze(
    image,
    extract_silhouette=True,   # Extract foreground mask
    detect_edges=True          # Detect edges
)
```

## Technical Details

### MediaPipe Integration

The Vision System uses MediaPipe for pose and landmark detection:

- **Pose**: 33 body landmarks in 3D space
- **Face Mesh**: 468 facial landmarks
- **Hands**: 21 hand landmarks per hand

All landmarks include normalized coordinates (0-1 range) and visibility/confidence scores.

### Coordinate Systems

- **Normalized coordinates**: 0.0 to 1.0 range, relative to image dimensions
- **Pixel coordinates**: Absolute pixel positions in image
- **3D coordinates**: Include depth (z) information from MediaPipe

### Performance Considerations

- MediaPipe initialization takes ~1-2 seconds on first use
- Analysis of a single image typically takes 50-200ms
- Comparison operations take 200-400ms
- Memory usage scales with image size and number of detected features

## API Reference

### VisionModule

**Methods:**
- `analyze(image, extract_silhouette=True, detect_edges=True)` → AnalysisResult
- `compare_to(canvas_image, reference_image)` → ComparisonResult
- `detect_pose_errors(canvas_image, reference_image=None)` → List[str]
- `highlight_areas_needing_refinement(canvas_image, reference_image)` → List[Dict]
- `close()` - Release resources

### ImageProcessor

**Methods:**
- `load_image(source)` → np.ndarray
- `to_rgb(image)` → np.ndarray
- `to_grayscale(image)` → np.ndarray
- `resize(image, width, height, max_size)` → np.ndarray
- `extract_silhouette(image, method)` → np.ndarray
- `detect_edges(image, low_threshold, high_threshold)` → np.ndarray
- `get_dimensions(image)` → Tuple[int, int]

### PoseDetector

**Methods:**
- `detect(image)` → Optional[PoseData]
- `detect_landmarks(image)` → Optional[PoseLandmarks]
- `visualize_pose(image, pose_data, color, thickness)` → np.ndarray
- `close()` - Release resources

### LandmarkDetector

**Methods:**
- `detect_face(image)` → Optional[FaceLandmarks]
- `detect_hands(image)` → List[HandLandmarks]
- `visualize_face(image, face_landmarks, color)` → np.ndarray
- `visualize_hands(image, hand_landmarks_list, color)` → np.ndarray
- `close()` - Release resources

### Comparator

**Methods:**
- `compare_poses(pose1, pose2, normalize)` → PoseMetrics
- `analyze_proportions(pose, standard_ratios)` → ProportionMetrics
- `analyze_symmetry(pose)` → SymmetryMetrics
- `calculate_edge_alignment(edges1, edges2)` → AlignmentMetrics

## Testing

The Vision System includes comprehensive tests:

```bash
# Run vision tests only
pytest tests/vision/ -v

# Run all tests (motor + vision)
pytest tests/ -v

# Run with coverage
pytest tests/vision/ --cov=vision --cov-report=html
```

All 32 vision tests pass, maintaining 100% compatibility with the existing 31 motor tests.

## Dependencies

- opencv-python >= 4.8.0
- mediapipe >= 0.10.0
- numpy >= 1.24.0
- Pillow >= 10.0.0

## Future Enhancements

Potential future improvements:

1. **GPU Acceleration**: Use TensorFlow GPU for faster MediaPipe inference
2. **Batch Processing**: Analyze multiple images in parallel
3. **Custom Pose Models**: Train domain-specific pose detection models
4. **Video Analysis**: Extend to video frame analysis
5. **Style Transfer Integration**: Connect with style_ai/ module
6. **Real-time Analysis**: Optimize for live canvas monitoring
7. **Advanced Metrics**: Add more anatomical correctness checks
8. **Semantic Segmentation**: Integrate semantic understanding of scene elements

## Troubleshooting

### Common Issues

**MediaPipe warnings**: The deprecation warnings from Google protobuf are harmless and can be ignored.

**Slow initialization**: First-time MediaPipe initialization downloads models. Subsequent calls are fast.

**No pose detected**: Ensure the image contains a clearly visible human figure with good lighting and contrast.

**Memory issues**: For large images, consider resizing before analysis:
```python
processor = ImageProcessor()
small_image = processor.resize(image, max_size=1024)
result = vision.analyze(small_image)
```

## License

Same license as the main Cerebrum project (MIT License).
