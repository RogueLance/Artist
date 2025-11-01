# End-to-End Testing Guide

This guide explains how to run end-to-end tests in the Cerebrum AI art platform and interpret the results.

## Overview

End-to-end (E2E) tests validate complete art generation workflows from start to finish, integrating all three core systems:

- **Motor System**: Drawing execution
- **Vision System**: Canvas analysis
- **Brain System**: Planning and decision-making

## Test Structure

### Test Directory

```
tests/e2e/
├── __init__.py           # E2E test framework
└── test_pipelines.py     # Pipeline tests
```

### Pipeline Types

Three main pipeline types are tested:

1. **Photo Reference Pipeline** - Transform photo references into stylized artwork
2. **Sketch Correction Pipeline** - Correct and refine rough sketches
3. **AI Image Pipeline** - Redraw AI-generated images with proper anatomy

## Running E2E Tests

### Basic Execution

Run all E2E tests:

```bash
pytest tests/e2e/ -v
```

Run specific test class:

```bash
pytest tests/e2e/test_pipelines.py::TestPhotoPipeline -v
```

Run single test:

```bash
pytest tests/e2e/test_pipelines.py::TestPhotoPipeline::test_photo_pipeline_basic -v
```

### With Coverage

```bash
pytest tests/e2e/ --cov=cerebrum --cov-report=html -v
```

### With Logging

```bash
pytest tests/e2e/ -v --log-cli-level=INFO
```

## Test Components

### 1. Pipeline Execution Tests

These tests verify that pipelines execute from start to finish:

```python
def test_photo_pipeline_basic(self):
    """Test basic photo pipeline execution."""
    photo = create_test_photo()
    
    pipeline = PhotoReferencePipeline(
        motor_backend="simulation",
        canvas_width=400,
        canvas_height=600,
        max_iterations=2
    )
    
    result = pipeline.execute(reference_image=photo)
    
    assert result is not None
    assert result.total_duration >= 0
    assert result.final_canvas is not None
```

**What to Check:**
- Pipeline completes without errors
- All expected stages execute
- Final canvas is generated
- Execution time is reasonable

### 2. Stage Validation Tests

These tests verify that all pipeline stages execute correctly:

```python
def test_photo_pipeline_stages(self):
    """Test that all expected stages are executed."""
    result = pipeline.execute(reference_image=photo)
    
    stage_names = [s.stage.value for s in result.stages]
    
    assert "initialization" in stage_names
    assert "analysis" in stage_names
    assert "completion" in stage_names
```

**What to Check:**
- All required stages execute
- Stages execute in correct order
- Each stage reports success/failure
- Stage timing is recorded

### 3. Metrics Collection Tests

These tests verify that meaningful metrics are collected:

```python
def test_pipeline_collects_metrics(self):
    """Test that pipelines collect metrics."""
    result = pipeline.execute(reference_image=photo)
    
    assert "total_stages" in result.metrics
    assert "successful_stages" in result.metrics
```

**What to Check:**
- Metrics are collected at pipeline level
- Metrics are collected at stage level
- Metrics are meaningful and accurate

### 4. Error Handling Tests

These tests verify graceful error handling:

```python
def test_pipeline_without_reference(self):
    """Test pipeline handles missing reference gracefully."""
    result = pipeline.execute(reference_image=None)
    
    assert result is not None
    assert result.total_duration >= 0
```

**What to Check:**
- Pipelines handle missing inputs
- Errors are logged appropriately
- System doesn't crash on edge cases

## Interpreting Results

### Successful Test Run

```
tests/e2e/test_pipelines.py::TestPhotoPipeline::test_photo_pipeline_basic PASSED
tests/e2e/test_pipelines.py::TestPhotoPipeline::test_photo_pipeline_stages PASSED
tests/e2e/test_pipelines.py::TestSketchPipeline::test_sketch_pipeline_basic PASSED
tests/e2e/test_pipelines.py::TestAIPipeline::test_ai_pipeline_basic PASSED

====== 4 passed in 45.23s ======
```

**Indicates:**
- All pipelines execute successfully
- System integration is working
- Ready for production use

### Test Failure

```
tests/e2e/test_pipelines.py::TestPhotoPipeline::test_photo_pipeline_basic FAILED

AssertionError: assert None is not None
```

**Indicates:**
- Pipeline failed to generate output
- Check logs for specific error
- May indicate Motor, Vision, or Brain failure

### Component-Specific Failures

#### Motor System Failure

```
ERROR: Stroke execution timeout
Component: motor
```

**Action:**
- Check Motor backend is available
- Verify canvas initialization
- Review stroke data validity

#### Vision System Failure

```
ERROR: Pose detection failed
Component: vision
confidence: 0.3
```

**Action:**
- Check input image quality
- Verify MediaPipe installation
- Review detection thresholds

#### Brain System Failure

```
ERROR: Task planning failed - no valid actions
Component: brain
```

**Action:**
- Review task creation logic
- Check action plan generation
- Verify context data

#### Integration Failure

```
ERROR: Motor-Vision sync issue
Component: integration
```

**Action:**
- Check system coordination
- Verify data passing between systems
- Review timing/synchronization

## Using the E2E Framework

### Running Complete Workflows

```python
from cerebrum.pipelines import PhotoReferencePipeline
from cerebrum.recording import SessionRecorder
from cerebrum.logging import FailureLogger

# Setup
recorder = SessionRecorder(session_name="test_run")
failure_logger = FailureLogger(session_name="test_run")

recorder.start()

try:
    # Execute pipeline
    pipeline = PhotoReferencePipeline(
        motor_backend="simulation",
        canvas_width=800,
        canvas_height=1000
    )
    
    result = pipeline.execute(reference_image=photo)
    
    # Record results
    if result.final_canvas is not None:
        recorder.record_snapshot(
            canvas_data=result.final_canvas,
            stage="completion",
            metrics=result.metrics
        )
    
    # Log failures
    if not result.success:
        for error in result.errors:
            failure_logger.log_pipeline_failure(
                description=error,
                severity=FailureSeverity.HIGH
            )

finally:
    recorder.stop()
    recorder.save("/tmp/test_results/")
    failure_logger.save("/tmp/test_results/")
```

### Analyzing Results

```python
# Load and analyze recording
recorder = SessionRecorder.load("/tmp/test_results/session_dir")

summary = recorder.get_summary()
print(f"Total snapshots: {summary['total_snapshots']}")
print(f"Duration: {summary['duration']}s")

# Generate visualizations
from cerebrum.recording import TimelapseGenerator

generator = TimelapseGenerator(recorder)
generator.generate_gif("progress.gif", fps=2)
generator.generate_image_grid("grid.png", cols=4)

# Load and analyze failures
failure_logger = FailureLogger.load("/tmp/test_results/session_failures.json")

stats = failure_logger.get_statistics()
print(f"Total failures: {stats['total_failures']}")
print(f"By component: {stats['by_component']}")

# Generate report
print(failure_logger.generate_report())
```

## Best Practices

### 1. Run Tests Regularly

- Run E2E tests before major changes
- Run after system updates
- Run as part of CI/CD pipeline

### 2. Monitor Performance

- Track execution times
- Compare against baselines
- Identify performance regressions

### 3. Analyze Failures

- Review failure logs after failed tests
- Classify failures by component
- Track resolution patterns

### 4. Maintain Test Data

- Keep diverse test inputs
- Include edge cases
- Update as system evolves

### 5. Document Results

- Save test outputs for comparison
- Document known issues
- Track improvements over time

## Troubleshooting

### Tests Running Slowly

**Possible Causes:**
- Large canvas sizes
- Too many iterations
- Complex reference images

**Solutions:**
- Reduce canvas size for tests
- Lower max_iterations
- Use simpler test images

### Intermittent Failures

**Possible Causes:**
- Timing issues
- Resource constraints
- Non-deterministic behavior

**Solutions:**
- Add retries for flaky tests
- Increase timeouts
- Use deterministic test data

### All Tests Failing

**Possible Causes:**
- System configuration issue
- Missing dependencies
- Environment problem

**Solutions:**
- Verify all dependencies installed
- Check system requirements
- Review logs for common errors

## Next Steps

After running E2E tests:

1. **Review Results**: Check which tests passed/failed
2. **Analyze Metrics**: Review performance and quality metrics
3. **Investigate Failures**: Use failure logger to diagnose issues
4. **Generate Reports**: Create documentation of test run
5. **Iterate**: Make improvements and retest

## See Also

- [Pipelines Documentation](PIPELINES.md) - Pipeline architecture and usage
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Examples](../examples/) - Example scripts and workflows
