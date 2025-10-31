# Pipeline System Documentation

Complete guide to the Cerebrum pipeline system for end-to-end art generation workflows.

## Overview

The pipeline system orchestrates complete art generation workflows by coordinating Motor, Vision, and Brain systems through multiple stages. Each pipeline type implements a specific workflow optimized for different input types.

## Architecture

### Base Pipeline

All pipelines inherit from `BasePipeline`, which provides:

- Stage-based execution flow
- Error handling and recovery
- Metrics collection
- Resource management

### Pipeline Stages

Every pipeline progresses through these stages:

1. **Initialization** - Setup systems and canvas
2. **Analysis** - Analyze input/reference
3. **Gesture** - Create initial sketch
4. **Structure** - Build anatomical structure
5. **Refinement** - Iterative improvements
6. **Detail** - Add fine details
7. **Stylization** - Apply artistic style
8. **Completion** - Final validation

## Pipeline Types

### 1. Photo Reference Pipeline

Transforms photo references into stylized artwork.

**Use Case:** Creating artwork from photo references while maintaining anatomical accuracy.

**Workflow:**
```
Photo → Pose Analysis → Gesture Sketch → Structure → Refinement → Details → Style → Output
```

**Example:**
```python
from cerebrum.pipelines import PhotoReferencePipeline

pipeline = PhotoReferencePipeline(
    motor_backend="simulation",
    canvas_width=800,
    canvas_height=1000,
    max_iterations=5,
    quality_threshold=0.75
)

result = pipeline.execute(
    reference_image="photo.jpg",
    goal="Create stylized portrait"
)

# Save result
from PIL import Image
Image.fromarray(result.final_canvas).save("output.png")
```

**Key Features:**
- Analyzes photo for pose and proportions
- Preserves anatomical accuracy
- Applies stylistic choices
- Iterative refinement based on similarity

**Configuration Options:**
- `motor_backend`: "simulation" or "krita"
- `canvas_width/height`: Output dimensions
- `max_iterations`: Maximum refinement cycles
- `quality_threshold`: Similarity threshold for completion

### 2. Sketch Correction Pipeline

Corrects and refines rough sketches with proper anatomy.

**Use Case:** Taking rough sketches and fixing proportion/anatomy errors while preserving gesture.

**Workflow:**
```
Rough Sketch → Issue Analysis → Construction Lines → Fix Structure → Refine → Details → Output
```

**Example:**
```python
from cerebrum.pipelines import SketchCorrectionPipeline

pipeline = SketchCorrectionPipeline(
    motor_backend="simulation",
    canvas_width=800,
    canvas_height=1000,
    max_iterations=5,
    quality_threshold=0.70
)

result = pipeline.execute(
    reference_image="rough_sketch.jpg",
    goal="Correct proportions and anatomy"
)
```

**Key Features:**
- Identifies structural issues
- Preserves original gesture energy
- Corrects major proportion errors
- Adds construction guides
- Refines iteratively

**Configuration Options:**
- Same as Photo Pipeline
- Lower quality threshold (0.70) since preserving sketch style

### 3. AI Image Pipeline

Redraws AI-generated images with corrected anatomy.

**Use Case:** Fixing AI-generated images that have anatomical errors (e.g., malformed hands, wrong proportions).

**Workflow:**
```
AI Image → Error Detection → Extract Composition → Redraw with Correct Anatomy → Style Match → Output
```

**Example:**
```python
from cerebrum.pipelines import AIImagePipeline

pipeline = AIImagePipeline(
    motor_backend="simulation",
    canvas_width=800,
    canvas_height=1000,
    max_iterations=5,
    quality_threshold=0.75
)

result = pipeline.execute(
    reference_image="ai_generated.png",
    goal="Redraw with correct anatomy"
)
```

**Key Features:**
- Detects anatomical errors
- Extracts good compositional elements
- Redraws with proper structure
- Preserves style intent
- Focuses on anatomical accuracy

**Common Issues Fixed:**
- Malformed hands and fingers
- Incorrect body proportions
- Asymmetry issues
- Joint placement errors
- Face/head proportions

## Pipeline Results

### PipelineResult Object

```python
@dataclass
class PipelineResult:
    success: bool                           # Overall success
    total_duration: float                   # Total execution time
    stages: List[StageResult]              # Results for each stage
    final_canvas: Optional[np.ndarray]     # Final output
    metrics: Dict[str, Any]                # Aggregate metrics
    errors: List[str]                      # Error messages
```

### StageResult Object

```python
@dataclass
class StageResult:
    stage: PipelineStage                   # Stage identifier
    success: bool                          # Stage success
    duration: float                        # Execution time
    metrics: Dict[str, Any]                # Stage-specific metrics
    notes: str                             # Additional notes
    canvas_state: Optional[np.ndarray]     # Canvas at this stage
```

### Accessing Results

```python
result = pipeline.execute(reference_image=photo)

# Check overall success
if result.success:
    print("Pipeline completed successfully!")

# Get specific stage result
analysis_result = result.get_stage_result(PipelineStage.ANALYSIS)
if analysis_result:
    print(f"Analysis took {analysis_result.duration:.2f}s")
    print(f"Metrics: {analysis_result.metrics}")

# Access metrics
print(f"Total stages: {result.get_metric('total_stages')}")
print(f"Successful stages: {result.get_metric('successful_stages')}")

# Review all stages
for stage_result in result.stages:
    status = "✓" if stage_result.success else "✗"
    print(f"{status} {stage_result.stage.value}: {stage_result.duration:.2f}s")
```

## Integration with Recording

Pipelines can be integrated with session recording:

```python
from cerebrum.pipelines import PhotoReferencePipeline
from cerebrum.recording import SessionRecorder, TimelapseGenerator

# Setup recording
recorder = SessionRecorder(session_name="artwork_creation")
recorder.start()

# Execute pipeline
pipeline = PhotoReferencePipeline(...)
result = pipeline.execute(reference_image=photo)

# Record final state
if result.final_canvas is not None:
    recorder.record_snapshot(
        canvas_data=result.final_canvas,
        stage="completion",
        metrics=result.metrics
    )

recorder.stop()

# Save and generate timelapse
recorder.save("/tmp/sessions/")

generator = TimelapseGenerator(recorder)
generator.generate_gif("timelapse.gif", fps=2)
generator.generate_image_grid("progress.png", cols=4)
```

## Integration with Failure Logging

Track failures during pipeline execution:

```python
from cerebrum.pipelines import PhotoReferencePipeline
from cerebrum.logging import FailureLogger, FailureSeverity

# Setup failure logging
failure_logger = FailureLogger(session_name="artwork_creation")

try:
    pipeline = PhotoReferencePipeline(...)
    result = pipeline.execute(reference_image=photo)
    
    # Log failures
    if not result.success:
        for error in result.errors:
            failure_logger.log_pipeline_failure(
                description=error,
                severity=FailureSeverity.HIGH
            )
    
    # Log stage-specific failures
    for stage_result in result.stages:
        if not stage_result.success:
            failure_logger.log_pipeline_failure(
                description=f"Stage {stage_result.stage.value} failed: {stage_result.notes}",
                severity=FailureSeverity.MEDIUM,
                stage=stage_result.stage.value
            )

except Exception as e:
    failure_logger.log_pipeline_failure(
        description=str(e),
        severity=FailureSeverity.CRITICAL
    )

finally:
    failure_logger.save("/tmp/logs/")
    print(failure_logger.generate_report())
```

## Custom Pipelines

You can create custom pipelines by extending `BasePipeline`:

```python
from cerebrum.pipelines.base_pipeline import BasePipeline, PipelineStage, StageResult

class CustomPipeline(BasePipeline):
    """Custom pipeline implementation."""
    
    def _stage_initialization(self, reference_image, goal, **kwargs):
        """Initialize your custom pipeline."""
        # Setup systems
        self.motor = MotorInterface(backend=self.motor_backend)
        self.vision = VisionModule()
        self.brain = BrainModule()
        
        # Custom initialization logic
        # ...
        
        return StageResult(
            stage=PipelineStage.INITIALIZATION,
            success=True,
            duration=0.0,
            notes="Custom initialization complete"
        )
    
    def _stage_analysis(self, reference_image, **kwargs):
        """Custom analysis stage."""
        # Your analysis logic
        # ...
        
        return StageResult(
            stage=PipelineStage.ANALYSIS,
            success=True,
            duration=0.0
        )
    
    # Implement other required stages...
```

## Performance Optimization

### Tips for Better Performance

1. **Reduce Canvas Size for Testing**
```python
pipeline = PhotoReferencePipeline(
    canvas_width=400,  # Smaller for faster execution
    canvas_height=600
)
```

2. **Limit Iterations**
```python
pipeline = PhotoReferencePipeline(
    max_iterations=2  # Fewer iterations for quick tests
)
```

3. **Adjust Quality Threshold**
```python
pipeline = PhotoReferencePipeline(
    quality_threshold=0.6  # Lower threshold for faster completion
)
```

4. **Use Simulation Backend**
```python
pipeline = PhotoReferencePipeline(
    motor_backend="simulation"  # Faster than Krita
)
```

## Best Practices

### 1. Pipeline Selection

- **Photo Reference**: Use for realistic source material
- **Sketch Correction**: Use for hand-drawn sketches needing fixes
- **AI Image**: Use for AI-generated images with anatomical issues

### 2. Quality Threshold

- Higher threshold (0.75-0.85): More refinement, better quality
- Lower threshold (0.60-0.70): Faster execution, acceptable quality
- Consider your use case when setting threshold

### 3. Iteration Count

- Start with 3-5 iterations
- Increase for complex images
- Monitor diminishing returns

### 4. Error Handling

- Always wrap pipeline execution in try-except
- Log failures for debugging
- Save intermediate results for analysis

### 5. Resource Management

- Pipelines automatically clean up resources
- Use context managers for recording/logging
- Monitor memory usage for large canvases

## Troubleshooting

### Pipeline Doesn't Complete

**Possible Causes:**
- Missing reference image
- System initialization failure
- Resource constraints

**Solutions:**
- Verify reference image is valid
- Check system dependencies
- Reduce canvas size

### Poor Output Quality

**Possible Causes:**
- Low quality threshold
- Insufficient iterations
- Poor reference quality

**Solutions:**
- Increase quality threshold
- Increase max_iterations
- Use higher quality reference

### Slow Execution

**Possible Causes:**
- Large canvas size
- Many iterations
- Complex reference

**Solutions:**
- Reduce canvas dimensions
- Lower max_iterations
- Optimize reference image

## See Also

- [End-to-End Testing Guide](END_TO_END_TESTING.md) - Testing documentation
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Examples](../examples/e2e_example.py) - Complete workflow examples
